// FILAMENT TRACKER - Arduino R4 WiFi + LCD Keypad Shield (USB version)

//  Libraries 
#include "HX711.h"              // Load cell amplifier library
#include <SPI.h>                // SPI communication (needed for RFID)
#include <MFRC522.h>            // RFID/NFC reader library
#include <LiquidCrystal.h>      // LCD display — built into Arduino IDE, no install needed

//  Load cell pins 
#define DT  2   // HX711 data pin
#define SCK 3   // HX711 clock pin

//  RFID pins 
#define SS_PIN  A1  // RFID SS slave select pin
#define RST_PIN A2  // RFID RST reset pin

//  LCD pin setup 
// The LCD Keypad Shield is always wired this way on Arduino:
// LiquidCrystal(RS, Enable, D4, D5, D6, D7)
LiquidCrystal lcd(8, 9, 4, 5, 6, 7);

// We divide the raw value printed during calibration by a known weight in grams
const float CALIBRATION_FACTOR = 408.18; // 

// Timing: how long to wait for weight to stabilize after scanning (ms)
const int WEIGHT_STABLE_DELAY = 5000; // 5 seconds

// Create objects 
HX711   cell; // Load cell ocject
MFRC522 mfrc522(SS_PIN, RST_PIN); // RFID reader object

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
  // Start serial communication with the computer through USB
  // This is both for debugging messages AND for sending data to Python  Serial.begin(9600);
  Serial.println(" Rastrejador de filaments (USB Serial mode) ");

  //  Initialise load cell 
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
  SPI.begin();   // Start the SPI bus
  mfrc522.PCD_Init();   // Initialize  RFID module

  lcdMessage("RFID preparat", "");
  Serial.println("Lector RFID preparat.");
  delay(1500);

  //  Ready screen — shown permanently until a scan happens 
  lcdMessage("Escaneja bobina", "adhesiu...");
  Serial.println("Llest. Si us plau, escaneja l'adhesiu NFC del filament.");
}

void loop() {

  // STEP 1: Check if a new NFC card/sticker is present
  if (!uidReady) {
    // Only look for a new card if we don't already have a UID waiting
    if (mfrc522.PICC_IsNewCardPresent() && mfrc522.PICC_ReadCardSerial()) {

      // Read the UID bytes and build a readable hexadecimal string (ex: "A3 F2 10 BC")
      scannedUID = ""; // Clear any previous UID
      for (byte i = 0; i < mfrc522.uid.size; i++) {
        if (i > 0) scannedUID += " ";        // Space between each byte
        if (mfrc522.uid.uidByte[i] < 0x10) scannedUID += "0"; // Add leading zero for single-digit hex values
        }
        scannedUID += String(mfrc522.uid.uidByte[i], HEX); // Add the hex value
      }
      scannedUID.toUpperCase(); // Make uppercase for consistency (ex: "A3" not "a3")

      // Mark that we now have a UID and need the weight next
      uidReady = true;

      // Show the UID on LCD
      // UID like "A3 F2 10 BC" is 11 chars — fits on a 16-char row
      Serial.print("NFC escanejat! UID: ");
      Serial.println(scannedUID);
      lcdMessage("UID escanejat:", scannedUID);  // Top: label, Bottom: the UID

      // End the RFID communication session with this sticker
      mfrc522.PICC_HaltA();
      mfrc522.PCD_StopCrypto1();

      // Tell worker to place filament on scale
      delay(1500); // Show UID for 1.5 seconds first
      Serial.println("Ara col·loca el filament a la bàscula...");
      lcdMessage("situa a bascula", "Pesant en 5s..");

      // Wait for the worker to place the filament on the scale and for it to stabilise
      delay(WEIGHT_STABLE_DELAY);
    }
  }

  //  STEP 2: If we have a UID ready, read the weight 
  if (uidReady) {

    // Show "measuring" message while reading
    lcdMessage("Mesurant...", "");

    // Read weight as average of 10 measurements for accuracy
    float weight = cell.get_units(10);
        // If weight is slightly negative due to drift, treat it as 0
    if (weight < 0) weight = 0; 

    Serial.print("Pes mesurat: ");
    Serial.print(weight, 1); // Print with 1 decimal place
    Serial.println("g");

    // Show the weight on LCD for a moment
    // Bottom row: e.g. "312.5 g"
    lcdMessage("Pes:", String(weight, 1) + " g");
    delay(2000); // Worker can see the reading for 2 seconds

    //  STEP 3: Send data to Python via USB Serial 
    // Format: DATA:UID:WEIGHT  — Python reads and parses this line
    // The Python script will look for lines starting with "DATA:" to know it's a reading
    Serial.print("DATA:"); // Marker so Python knows this is a data line (not a debug message)
    Serial.print(scannedUID); // The NFC sticker UID
    Serial.print(":"); // Separator between UID and weight
    Serial.println(weight, 1); // The weight value (println adds a newline at the end)

    // Show "Sending..." while the data goes to Python
    lcdMessage("Enviant dades", "a base de dades");
    delay(2000);

    //  Check if weight is low and warn the worker on screen 
    if (weight < 150.0) {
      // Flash a warning on the LCD so the worker knows this roll is nearly empty
      lcdMessage("!! LOW STOCK !!", String(weight, 1) + "g restants");
      Serial.println("⚠ AVÍS!!!!: El pes està per sota del llindar mínim!");
      delay(3000); // Show warning for 3 seconds
    }

    // Reset so we are ready for the next filament
    uidReady   = false;
    scannedUID = "";

    lcdMessage("Fet! Scan next", "filament...");
    Serial.println("Fet. Pots escanejar el següent filament o el mateix de nou.");
    delay(2000); // Small pause before accepting a new scan

    // Return to the main idle message
    lcdMessage("Escaneja bobina", "adhesiu...");
  }

  // Save power: put load cell in low-power mode so energy is saved
  cell.power_down();
  delay(100);
  cell.power_up();
}
