/*
  FILAMENT TRACKER - Arduino R4 WiFi + LCD Keypad Shield (USB version)
*/

//  Libraries 
#include "HX711.h"              // Load cell amplifier
#include <SPI.h>                // SPI bus (needed for RFID)
#include <MFRC522.h>            // RFID/NFC reader
#include <LiquidCrystal.h>      // LCD display — built into Arduino IDE, no install needed

//  Load cell pins 
#define DT  2   // HX711 data
#define SCK 3   // HX711 clock

//  RFID pins (moved to avoid conflict with LCD shield) 
#define SS_PIN  A1  // RFID SS — moved from 10 to A1
#define RST_PIN A2  // RFID RST — moved from 9 to A2

//  LCD pin setup 
// The LCD Keypad Shield is always wired this way on Arduino:
// LiquidCrystal(RS, Enable, D4, D5, D6, D7)
LiquidCrystal lcd(8, 9, 4, 5, 6, 7);

//  Calibration factor — S'ha de canviar
const float CALIBRATION_FACTOR = 2280.0; // <-- replace with your value

// Timing: how long to wait for weight to stabilize after scanning (ms)
const int WEIGHT_STABLE_DELAY = 3000; // 3 seconds

// Create objects 
HX711   cell;
MFRC522 mfrc522(SS_PIN, RST_PIN);

//  Global variables 
String scannedUID = "";    // Stores the last scanned NFC tag UID
bool   uidReady   = false; // True when a UID has been scanned and is waiting for weight

// lcdMessage()
// Helper function to show a message on the LCD.
// line1 = top row, line2 = bottom row (use "" to leave blank)
// The display is 16 characters wide — longer text gets cut off.
void lcdMessage(String line1, String line2) {
  lcd.clear();         // Clear whatever was on screen before
  lcd.setCursor(0, 0); // Move cursor to start of top row
  lcd.print(line1);    // Print first line
  lcd.setCursor(0, 1); // Move cursor to start of bottom row
  lcd.print(line2);    // Print second line
}

void setup() {
  // Start serial (still useful for debugging with Serial Monitor)
  Serial.begin(9600);
  Serial.println(" Rastrejador de filaments (USB Serial mode) ");

  //  Start the LCD 
  lcd.begin(16, 2);        // Tell library the display is 16 columns, 2 rows
  lcdMessage("Filament", "Tracker v1.0");  // Splash screen on startup
  delay(2000);             // Show splash for 2 seconds

  //  Initialise load cell 
  cell.begin(DT, SCK);              // Tell HX711 which pins to use
  cell.set_scale(CALIBRATION_FACTOR); //posar numero que treiem de calibració: num.f
  cell.tare();  // Zero the scale

  lcdMessage("Bascula llesta", "Zeroed OK");
  Serial.println("Cèl·lula de càrrega preparada.");
  delay(1500);

  //  Initialise RFID reader 
  SPI.begin();
  mfrc522.PCD_Init();

  lcdMessage("RFID preparat", "");
  Serial.println("Lector RFID preparat.");
  delay(1500);

  //  Ready screen — shown permanently until a scan happens 
  lcdMessage("Escaneja bobina", "adhesiu...");
  Serial.println("Llest. Si us plau, escaneja l'adhesiu NFC del filament.");
}

void loop() {

  //  STEP 1: Wait for an NFC scan 
  if (!uidReady) {
    // Only look for a new card if we don't already have a UID waiting
    if (mfrc522.PICC_IsNewCardPresent() && mfrc522.PICC_ReadCardSerial()) {

      // Build the UID string from the bytes read
      scannedUID = "";
      for (byte i = 0; i < mfrc522.uid.size; i++) {
        if (i > 0) scannedUID += " ";
        if (mfrc522.uid.uidByte[i] < 0x10) scannedUID += "0"; // leading zero
        scannedUID += String(mfrc522.uid.uidByte[i], HEX);
      }
      scannedUID.toUpperCase();

      uidReady = true;

      // Show the UID on LCD
      // UID like "A3 F2 10 BC" is 11 chars — fits on a 16-char row
      Serial.print("NFC escanejat! UID: ");
      Serial.println(scannedUID);
      lcdMessage("UID escanejat:", scannedUID);  // Top: label, Bottom: the UID

      // End the RFID communication session
      mfrc522.PICC_HaltA();
      mfrc522.PCD_StopCrypto1();

      // Tell worker to place filament on scale
      delay(1500); // Show UID for 1.5 seconds first
      Serial.println("Ara col·loca el filament a la bàscula...");
      lcdMessage("situa a bascula", "Pesant en 3s..");

      // Wait for filament to be placed and weight to stabilise
      delay(WEIGHT_STABLE_DELAY);
    }
  }

  //  STEP 2: Read the weight 
  if (uidReady) {

    // Show "measuring" message while reading
    lcdMessage("Mesurant...", "");

    // Take average of 10 readings
    float weight = cell.get_units(10);
    if (weight < 0) weight = 0; // Clamp negatives to zero

    Serial.print("Pes mesurat: ");
    Serial.print(weight, 1);
    Serial.println("g");

    // Show the weight on LCD for a moment
    // Bottom row: e.g. "312.5 g"
    lcdMessage("Pes:", String(weight, 1) + " g");
    delay(2000); // Worker can see the reading for 2 seconds

    //  STEP 3: Send data to Python via USB Serial 
    // Format: DATA:UID:WEIGHT  — Python reads and parses this line
    Serial.print("DATA:");
    Serial.print(scannedUID);
    Serial.print(":");
    Serial.println(weight, 1);

    // Show "Sending..." while the data goes to Python
    lcdMessage("Enviant dades", "a base de dades");
    delay(1000);

    //  Check if weight is low and warn the worker on screen 
    if (weight < 200.0) {
      // Flash a warning on the LCD so the worker knows this roll is nearly empty
      lcdMessage("!! LOW STOCK !!", String(weight, 1) + "g restants");
      Serial.println("⚠ AVÍS!!!!: El pes està per sota del llindar mínim!");
      delay(3000); // Show warning for 3 seconds
    }

    // Reset and go back to waiting for the next scan
    uidReady   = false;
    scannedUID = "";

    lcdMessage("Fet! Scan next", "filament...");
    Serial.println("Fet. Pots escanejar el següent filament o el mateix de nou.");
    delay(2000);

    // Return to the main idle message
    lcdMessage("Escaneja bobina", "adhesiu...");
  }

  // Save power on load cell while idle
  cell.power_down();
  delay(100);
  cell.power_up();
}
