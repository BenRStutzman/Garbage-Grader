/* 
 Example using the SparkFun HX711 breakout board with a scale
 By: Nathan Seidle
 SparkFun Electronics
 Date: November 19th, 2014
 License: This code is public domain but you buy me a beer if you use this and we meet someday (Beerware license).

 This example demonstrates basic scale output. See the calibration sketch to get the calibration_factor for your
 specific load cell setup.

 This example code uses bogde's excellent library:"https://github.com/bogde/HX711"
 bogde's library is released under a GNU GENERAL PUBLIC LICENSE

 The HX711 does one thing well: read load cells. The breakout board is compatible with any wheat-stone bridge
 based load cell which should allow a user to measure everything from a few grams to tens of tons.
 Arduino pin 2 -> HX711 CLK
 3 -> DAT
 5V -> VCC
 GND -> GND

 The HX711 board can be powered from 2.7V to 5V so the Arduino 5V power should be fine.

*/

#include "HX711.h"

#define calibration_factor -26000.0 //This value is obtained using the SparkFun_HX711_Calibration sketch

#define DOUT  3
#define CLK  2

const byte avg_len = 5;
unsigned long counter;
float last10[avg_len];
float avg;
float sum;
float delta;

HX711 scale;

void setup() {
  Serial.begin(9600);
  Serial.println("HX711 scale demo");

  scale.begin(DOUT, CLK);
  scale.set_scale(calibration_factor); //This value is obtained by using the SparkFun_HX711_Calibration sketch
  scale.tare(); //Assuming there is no weight on the scale at start up, reset the scale to 0

  Serial.println("Readings:");
}

void loop() {
  last10[counter % avg_len] = scale.get_units();
  sum = 0;
  for (int i = 0; i < avg_len; i++) {
    sum += last10[i];
  }
  if (counter % avg_len == 0) {
    delta = (sum / avg_len) - avg;
    avg = sum / avg_len;
    Serial.print("Reading: ");
    Serial.print(avg, 4); //scale.get_units() returns a float
    Serial.print(" kg"); //You can change this to kg but you'll need to refactor the calibration_factor
    Serial.print("\t\t Delta was: ");
    if (delta > 0) { Serial.print(" "); }
    Serial.print(delta, 5);
    if (delta > 0.020) { Serial.print("\t\t Something was added!?"); }
    Serial.println();
  }
  counter++;
}
