/******************************************************************
 This is an example for the Adafruit RA8875 Driver board for TFT displays
 ---------------> http://www.adafruit.com/products/1590
 The RA8875 is a TFT driver for up to 800x480 dotclock'd displays
 It is tested to work with displays in the Adafruit shop. Other displays
 may need timing adjustments and are not guanteed to work.

 Adafruit invests time and resources providing this open
 source code, please support Adafruit and open-source hardware
 by purchasing products from Adafruit!

 Written by Limor Fried/Ladyada for Adafruit Industries.
 BSD license, check license.txt for more information.
 All text above must be included in any redistribution.
 ******************************************************************/


#include <SPI.h>
#include "Adafruit_GFX.h"
#include "Adafruit_RA8875.h"

// Library only supports hardware SPI at this time
// Connect SCLK to UNO Digital #13 (Hardware SPI clock)
// Connect MISO to UNO Digital #12 (Hardware SPI MISO)
// Connect MOSI to UNO Digital #11 (Hardware SPI MOSI)
#define RA8875_INT 3
#define RA8875_CS 10
#define RA8875_RESET 9

#include "DHT.h"
#define DHTPIN 2
#define DHTTYPE DHT11

DHT dht(DHTPIN, DHTTYPE);

// defines pins numbers
const int trigPin = 3;
const int echoPin = 5;
// defines variables
long duration;
int distance;
Adafruit_RA8875 tft = Adafruit_RA8875(RA8875_CS, RA8875_RESET);
uint16_t tx, ty;

void setup()
{
  Serial.begin(9600);
    dht.begin(); // initialize the sensor
  Serial.println("RA8875 start");
  pinMode(trigPin, OUTPUT); // Sets the trigPin as an Output
  pinMode(echoPin, INPUT); // Sets the echoPin as an Input

  /* Initialize the display using 'RA8875_480x80', 'RA8875_480x128', 'RA8875_480x272' or 'RA8875_800x480' */
  if (!tft.begin(RA8875_800x480)) {
    Serial.println("RA8875 Not Found!");
    while (1);
  }

  tft.displayOn(true);
  tft.GPIOX(true);      // Enable TFT - display enable tied to GPIOX
  tft.PWM1config(true, RA8875_PWM_CLK_DIV1024); // PWM output for backlight
  tft.PWM1out(255);
  
  // tft.fillScreen(RA8875_BLACK);

  /* Switch to text mode */
  tft.textMode();
  tft.cursorBlink(32);


  /* Set a solid for + bg color ... */

  /* ... or a fore color plus a transparent background */


  /* Set the cursor location (in pixels) */
  tft.textSetCursor(10, 10);

  /* Render some text! */
  char string[25] = "KWADWO AMIR BISHOY ROCK";
  // tft.textTransparent(RA8875_WHITE);
  // tft.textWrite(string);
  // tft.textColor(RA8875_WHITE, RA8875_RED);
  // tft.textWrite(string);
  // tft.textTransparent(RA8875_CYAN);
  // tft.textWrite(string);
  // tft.textTransparent(RA8875_GREEN);
  // tft.textWrite(string);
  // tft.textColor(RA8875_YELLOW, RA8875_CYAN);
  // tft.textWrite(string);
  // tft.textColor(RA8875_BLACK, RA8875_MAGENTA);
  // tft.textWrite(string);

  /* Change the cursor location and color ... */
  // tft.textSetCursor(100, 100);
  // tft.textTransparent(RA8875_RED);
  // // /* If necessary, enlarge the font */
  // tft.textEnlarge(1);
  // // /* ... and render some more text! */
  // // tft.textWrite(string);
  // tft.textSetCursor(100, 150);
  // tft.textEnlarge(2);
  // tft.textWrite(string);
}

void loop()
{
    // Clears the trigPin
  digitalWrite(trigPin, LOW);
  delayMicroseconds(2);
  // Sets the trigPin on HIGH state for 10 micro seconds
  digitalWrite(trigPin, HIGH);
  delayMicroseconds(10);
  digitalWrite(trigPin, LOW);
  // Reads the echoPin, returns the sound wave travel time in microseconds
  duration = pulseIn(echoPin, HIGH);
  // Calculating the distance
  distance = duration * 0.034 / 2;
  // Prints the distance on the Serial Monitor
  Serial.print("Distance: ");
  Serial.println(distance);

  // read humidity
  float humi  = dht.readHumidity();
  // read temperature as Celsius
  float tempC = dht.readTemperature();
  // read temperature as Fahrenheit
  float tempF = dht.readTemperature(true);

  // check if any reads failed
  if (isnan(humi) || isnan(tempC) || isnan(tempF)) {
    Serial.println("Failed to read from DHT sensor!");
  } else {
    Serial.print("Humidity: ");
    Serial.print(humi);
    Serial.print("%");

    Serial.print("  |  "); 

    Serial.print("Temperature: ");
    Serial.print(tempC);
    Serial.print("°C ~ ");
    Serial.print(tempF);
    Serial.println("°F");
  }

  tft.textTransparent(RA8875_RED);
  // /* If necessary, enlarge the font */
  tft.textEnlarge(1);
  // /* ... and render some more text! */
  // tft.textWrite(string);
  tft.textSetCursor(100, 100);
  tft.textEnlarge(2);
  tft.textWrite("Distance: ");
  char distance_string[5];
  itoa(distance,distance_string, 10);
  tft.textWrite(distance_string);
  tft.textWrite(" cm");

  tft.textWrite("     Tmp: ");
  itoa(tempC,distance_string, 10);
  tft.textWrite(distance_string);
  tft.textWrite(" C");

  tft.textWrite("           Humidity: ");
  itoa(humi,distance_string, 10);
  tft.textWrite(distance_string);
  tft.textWrite(" %");

  delay(3000);
  tft.fillScreen(RA8875_BLACK);
}
