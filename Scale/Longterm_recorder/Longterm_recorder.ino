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
#define DOUT  3
#define CLK  2

#define calibration_factor -22500.0 //This value is obtained using the SparkFun_HX711_Calibration sketch (or just by testing weights in this program and adjusting)

const byte num_readings = 20;
const byte num_avgs = 20;
const int start_delay = 30000;
const int dump_time = 500;
const float sensitivity = 0.02;

boolean find_weight;
unsigned long counter;
unsigned long last_trigger;
unsigned long now_time;
unsigned long then_time;
float last_readings[num_readings];
float last_avgs[num_avgs];
float reading;
float avg;
float sum;
float delta;
float item_weight;
float prev_avg;

HX711 scale;

void take_reading() {
  reading = scale.get_units();
  sum -= last_readings[counter % num_readings];
  sum += reading;
  avg = sum / num_readings;
  delta = avg - last_avgs[counter % num_avgs];
}

void detect_food() {
  if (delta > sensitivity && find_weight == false) {
    //Serial.println();
    //Serial.print("\t\tfood added: ");
    prev_avg = last_avgs[counter % num_avgs];
    find_weight = true;
    item_weight = delta;
    last_trigger = millis();
  }
}

void measure_weight() {
  if (find_weight) {
    if (delta > sensitivity) { last_trigger = millis(); }
    if (long(millis() - last_trigger) < dump_time) {
      if (avg - prev_avg > item_weight) { item_weight = avg - prev_avg; }
    } else {
      //Serial.print(item_weight * 1000, 2); Serial.print(" g");
      //Serial.println();
      //Serial.println();
      find_weight = false;
      reset_readings();
    }
  }
}

void reset_readings() {
  for (int i = 0; i < num_readings; i++) {
    last_readings[i] = reading;
    last_avgs[i] = reading;
  }
  sum = reading * num_readings;
}

void setup() {
  Serial.begin(9600);

  scale.begin(DOUT, CLK);
  scale.set_scale(calibration_factor); //This value is obtained by using the SparkFun_HX711_Calibration sketch
  //scale.tare(); //Assuming there is no weight on the scale at start up, reset the scale to 0

  Serial.println("Initializing...");
  for(int i = 0; i < 80; i++) {
    Serial.print("|");
    scale.get_units();
    delay(start_delay / 80);
  }
  //Serial.println();
  scale.tare();
  reading = scale.get_units();
  reset_readings();
  //Serial.print("Release the crackers!");
  //Serial.println();
  //Serial.println();
  Serial.println("Time (h),Reading (kg),Average (kg),Delta (g)");

}

void loop() {

  take_reading();
  detect_food();
  measure_weight();
/*
  if (counter % 50 == 0 && not find_weight) {
    Serial.print("total weight: "), Serial.print(avg); Serial.print(" kg");
    Serial.println();
  }
  */
  Serial.print(avg, 4); Serial.print("\t");
  Serial.println(delta, 4);
  
  //Stuff To print for diagnosis
  /*
  now_time = millis();
  if (now_time - then_time > 500 & now_time % 1000 < 500) {
    then_time = now_time;
    //Serial.print(float((unsigned long)(now_time / 1000)) / 3600, 4); Serial.print(",");
    //Serial.print("Reading: ");
    //if (reading > 0) { Serial.print(" "); }
    Serial.print(reading, 4); Serial.print(","); //Serial.print(" kg");
    //Serial.print("   Moving avg: ");
    //if (avg > 0) { Serial.print(" "); }
    Serial.print(avg, 4); Serial.print(","); //Serial.print(" kg");
    //Serial.print("   Delta: ");
    //if (delta > 0) { Serial.print(" "); }
    Serial.print(delta * 1000, 1); //Serial.print(" g");
    Serial.println();
  }
  */
  
  last_readings[counter % num_readings] = reading;
  last_avgs[counter % num_avgs] = avg;
  counter++;  
  
}
