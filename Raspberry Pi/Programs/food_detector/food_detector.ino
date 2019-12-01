#include "HX711.h"
#define DOUT  3
#define CLK  2

#define calibration_factor -22500.0 //This value is obtained using the SparkFun_HX711_Calibration sketch (or just by testing weights in this program and adjusting)

const byte num_readings = 20;
const byte num_avgs = 20;
const int start_delay = 300; //in cycles, which are about 0.1 seconds
const int dump_time = 500; //in ms
const float sensitivity = 0.020; //in kg, the lightest weight it will detect
const float bin_weight = 3;
const byte check_freq = 5; //in minutes

boolean bin_removed;
boolean find_weight;
long check_interval = check_freq * 59545;
unsigned long counter;
unsigned long last_trigger;
unsigned long last_check;
float last_readings[num_readings];
float last_avgs[num_avgs];
float reading;
float avg;
float sum;
float delta;
float item_weight;
float prev_avg;
float max_weight[2];

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
    Serial.println("food added");
    //Serial.println();
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
      Serial.println(item_weight * 1000, 2);
      //Serial.println();
      find_weight = false;
      reset_readings();
    }
  }
}

void reset_scale() {
  if (not bin_removed) { Serial.println("scale reset"); }
  for(int i = 0; i < start_delay; i++) { scale.get_units(); }
  if (bin_removed) {
    float amount_removed = max_weight[0] - scale.get_units();
    if (amount_removed < 1) { Serial.println(0, 3); }
    else { Serial.println(amount_removed, 3); }
  }
  scale.tare();
  reset_readings();
  counter = 1;
  max_weight[0] = 0.0;
  max_weight[1] = 0.0;
  find_weight = false;
  if (bin_removed) {
    Serial.println("scale reset");
    bin_removed = false;
  }
  Serial.println(reading, 3);
}

void reset_readings() {
  
  reading = scale.get_units();
  for (int i = 0; i < num_readings; i++) {
    last_readings[i] = reading;
    last_avgs[i] = reading;
  }
  sum = reading * num_readings;
  
}

void detect_removal() {
  if (avg < -bin_weight / 2 && !find_weight) {
    //if (find_weight) { Serial.println("0.00"); }
    Serial.println("bin removed");
    int i = 0;
    while (i < 100) {
      //Serial.println("delta:");
      //Serial.println(delta, 3);
      take_reading();
      last_readings[counter % num_readings] = reading;
      last_avgs[counter % num_avgs] = avg;
      counter++;
      if (delta < -sensitivity) {
        i = 0;
      } else { i++; }
    }
    float base_weight = avg;
    bin_removed = true;
    while (avg < base_weight + bin_weight / 2 && avg < -bin_weight / 2) {
      //Serial.println(avg, 3);
      take_reading();
      last_readings[counter % num_readings] = reading;
      last_avgs[counter % num_avgs] = avg;
      counter++;
    }
    reset_scale();
  }
}

void occasional_checks() {
  // stuff to check every check_freq minutes
  if (millis() - last_check >= check_interval) {
    Serial.println("weight checked");
    Serial.println(avg, 3);
    last_check += check_interval;
    max_weight[0] = max_weight[1];
    max_weight[1] = avg;
    //String input = Serial.readString();
    //Serial.println(input);
    if (Serial.readString() == "reset scale 1") {
      reset_scale();
    }
  }
}

void setup() {
  Serial.begin(9600);

  scale.begin(DOUT, CLK);
  scale.set_scale(calibration_factor); //This value is obtained by using the SparkFun_HX711_Calibration sketch
  reset_scale();

}

void loop() {

  occasional_checks();
  detect_removal();
  take_reading();
  detect_food();
  measure_weight();

  last_readings[counter % num_readings] = reading;
  last_avgs[counter % num_avgs] = avg;
  counter++;
  
  //Serial.println(avg, 3);

  /*
  //Stuff To print for diagnosis
  Serial.print("Reading: ");
  if (reading > 0) { Serial.print(" "); }
  Serial.print(reading, 4); Serial.print(" kg");
  Serial.print("   Moving avg: ");
  if (avg > 0) { Serial.print(" "); }
  Serial.print(avg, 4); Serial.print(" kg");
  Serial.print("   Delta: ");
  if (delta > 0) { Serial.print(" "); }
  Serial.print(delta * 1000, 1); Serial.print(" g");
  Serial.println();
  */
  
  
}
