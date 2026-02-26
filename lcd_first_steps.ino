#include <LiquidCrystal.h>

#define IS_ARDUINO 1
#define IS_ESP32   !IS_ARDUINO

#define IS_KEYPAD_D1ROBOT  0
#define IS_KEYPAD_VELLEMAN !IS_KEYPAD_D1ROBOT

//LiquidCrystal lcd(8, 9, 4, 5, 6, 7);
#if IS_ARDUINO
#define PIN_RS 8
#define PIN_EN 9
#define PIN_D4 4
#define PIN_D5 5
#define PIN_D6 6
#define PIN_D7 7
#endif

#if IS_ESP32
#define PIN_RS 12
#define PIN_EN 13
#define PIN_D4 17
#define PIN_D5 16
#define PIN_D6 27
#define PIN_D7 14
#endif

LiquidCrystal lcd(PIN_RS, PIN_EN, PIN_D4, PIN_D5, PIN_D6, PIN_D7);
int lcd_key     = 0;
int lcd_key_old = 1;
int adc_key_in  = 0;

#define BUTTON_RIGHT  0
#define BUTTON_UP     1
#define BUTTON_DOWN   2
#define BUTTON_LEFT   3
#define BUTTON_SELECT 4
#define BUTTON_NONE   5
c:\Users\Juanma Bailen\DATOS\Proyectos\EXO\enhance_arduino_codes\Hybrid control\main\a_driver_dictionary.ino
#define LINE_UP   0
#define LINE_DOWN 1

#define A0 0

int read_LCD_buttons() {

#if IS_ARDUINO //valores para ARDUINO UNO R3
  adc_key_in = analogRead(A0);
#endif

#if IS_ESP32 //valores para WEMOS D1 R32
  adc_key_in = analogRead(2); //IO2
#endif

#if IS_KEYPAD_D1ROBOT //valores para KEYPAD D1ROBOT
  if (adc_key_in > 900) return BUTTON_NONE;
  if (adc_key_in <  50) return BUTTON_RIGHT;
  if (adc_key_in < 250) return BUTTON_UP;
  if (adc_key_in < 450) return BUTTON_DOWN;
  if (adc_key_in < 650) return BUTTON_LEFT;
  if (adc_key_in < 850) return BUTTON_SELECT;
#endif

#if IS_KEYPAD_VELLEMAN //valores para KEYPAD Velleman
  if (adc_key_in > 800) return BUTTON_NONE;
  if (adc_key_in <  50) return BUTTON_RIGHT;
  if (adc_key_in < 150) return BUTTON_UP;
  if (adc_key_in < 300) return BUTTON_DOWN;
  if (adc_key_in < 500) return BUTTON_LEFT;
  if (adc_key_in < 750) return BUTTON_SELECT;
#endif

  return BUTTON_NONE;

}

void setup() {

  // Inicializar el LCD
  lcd.begin(16, 2);
  Serial.begin(9600);

}

void loop() {

  lcd.setCursor(0, LINE_UP);
  //0123456789012345
  //ADC = 1024
  lcd.print("ADC=");
  lcd.print(adc_key_in);
  Serial.println(adc_key_in);

  lcd_key = read_LCD_buttons();

  if (lcd_key_old != lcd_key) {
    lcd_key_old = lcd_key;
    lcd.setCursor(0, LINE_UP); lcd.print("                ");
    //0123456789012345
    //SELECT
    lcd.setCursor(0, LINE_DOWN);
    switch (lcd_key) {
      default            : 
      case BUTTON_NONE   : lcd.print("NONE  "); break;
      case BUTTON_RIGHT  : lcd.print("RIGHT "); break;
      case BUTTON_LEFT   : lcd.print("LEFT  "); break;
      case BUTTON_UP     : lcd.print("UP    "); break;
      case BUTTON_DOWN   : lcd.print("DOWN  "); break;
      case BUTTON_SELECT : lcd.print("SELECT"); break;
    }
  }

  //0123456789012345
  //        123456 s
  lcd.setCursor(9, LINE_DOWN);
  lcd.print(millis()/1000);
  lcd.print(" s");

}
