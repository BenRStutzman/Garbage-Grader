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

#define calibration_factor -23000.0 //This value is obtained using the SparkFun_HX711_Calibration sketch

#define DOUT  3
#define CLK  2

const byte num_readings = 20;
const byte num_avgs = 20;
unsigned long counter;
float last_readings[num_readings];
float last_avgs[num_avgs];
float reading;
float avg;
float sum;
float delta;
int dump_time = 500;
float sensitivity = 0.02;
int start_delay = 30000;
unsigned long last_trigger;
float item_weight;
//float prev_item_weight;
boolean find_weight;
float predicted;
float prev_avg;

HX711 scale;

void reset_readings(float cur_weight) {
  for (int i = 0; i < num_readings; i++) {
    last_readings[i] = cur_weight;
    last_avgs[i] = cur_weight;
    sum = cur_weight * num_readings;
  }
}

void setup() {
  Serial.begin(9600);

  scale.begin(DOUT, CLK);
  scale.set_scale(calibration_factor); //This value is obtained by using the SparkFun_HX711_Calibration sketch
  scale.tare(); //Assuming there is no weight on the scale at start up, reset the scale to 0

  Serial.println("Initializing...");
  for(int i = 0; i < 80; i++) {
    Serial.print("|");
    delay(start_delay / 80);
  }
  Serial.println();
  reading = scale.get_units();
  reset_readings(reading);
  Serial.print("Release the crackers!");
  Serial.println();
}

void loop() {
  reading = scale.get_units();
  
  sum -= last_readings[counter % num_readings];
  last_readings[counter % num_readings] = reading;
  sum += reading;
  avg = sum / num_readings;
  delta = avg - last_avgs[counter % num_avgs];
  predicted = reading - last_avgs[counter % num_avgs];
  if (find_weight) {
    if (delta > sensitivity) { last_trigger = millis(); }
    if (long(millis() - last_trigger) < dump_time) {
      if (avg - prev_avg > item_weight) { item_weight = avg - prev_avg; }
    } else {
      Serial.print(item_weight * 1000, 2);
      Serial.print(" g");
      Serial.println();
      find_weight = false;
      reset_readings(avg);
    }
  }
  /*
  Serial.print("Reading: "); Serial.print(reading, 4);
  Serial.print("\tMoving avg: ");
  Serial.print(avg, 4); //scale.get_units() returns a float
  Serial.print(" kg"); //You can change this to kg but you'll need to refactor the calibration_factor
  Serial.print("\tDelta: ");
  if (delta > 0) { Serial.print(" "); }
  Serial.print(delta * 1000, 1); Serial.print(" g");
  Serial.println();
  */
  if (delta > sensitivity && find_weight == false) {
    Serial.print("food added: ");
    prev_avg = last_avgs[counter % num_avgs];
    find_weight = true;
    item_weight = delta;
    last_trigger = millis();
  }

  last_avgs[counter % num_avgs] = avg;
  counter++;
}
