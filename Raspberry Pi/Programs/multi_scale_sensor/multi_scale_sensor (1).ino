#include "HX711.h"
#define DOUT_CAM     3
#define CLK_CAM      2
#define DOUT_MIDDLE  5
#define CLK_MIDDLE   4
#define DOUT_FAR     8
#define CLK_FAR      7

#define calibration_factor_1 -20690.0 //This value is obtained using the SparkFun_HX711_Calibration sketch (or just by testing weights in this program and adjusting)
#define calibration_factor_2 -21430.0
#define calibration_factor_3 -24170.0

const byte num_readings = 20; //how many readings at a time it averages
const byte num_avgs = 20; //how many averages back it compares for a "delta"
const int start_delay = 300; //startup time, in cycles, which are about 0.1 seconds
const int dump_time = 1000; //time it waits before assuming a person's done dumping, in ms
const float sensitivity = 0.020; //in kg, the lightest weight it will detect
const float bin_weight = 10; //in kg
const byte check_freq = 5; //in minutes, how often it checks the total weight of the scales

boolean bin_removed;
boolean find_weight;
boolean minor_scale_setup = false;
int num_minor_scale_measure = 0;
long check_interval = check_freq * 60000 - 2000;
unsigned long counter;
unsigned long last_trigger;
unsigned long last_check;
float last_readings[num_readings];
float last_avgs[num_avgs];
float reading;
float avg;
float sum;
float sum_trash;
float sum_far;
float delta;
float item_weight;
float prev_avg;
float max_weight[2];

HX711 scale;
HX711 scale_trash;
HX711 scale_far;


void take_reading() {
  reading = scale.get_units();
  sum -= last_readings[counter % num_readings];
  sum += reading;
  avg = sum / num_readings;
  delta = avg - last_avgs[counter % num_avgs];


  // only record the data from the other scales if we are about to report the data
  // happens for 2 sec every check_freq minutes
  if(minor_scale_setup){
   sum_trash += scale_trash.get_units();
   sum_far += scale_far.get_units();
   num_minor_scale_measure++;
  }
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
    if (amount_removed < 0.1) { Serial.println(0, 3); }
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

void zero_scales() {
  Serial.println("scales reset");
  for(int i = 0; i < start_delay; i++) {
    scale.get_units();
    scale_trash.get_units();
    scale_far.get_units();
  }
  scale.tare();
  scale_trash.tare();
  scale_far.tare();
  
  reset_readings();
  counter = 1;
  max_weight[0] = 0.0;
  max_weight[1] = 0.0;
  find_weight = false;
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
    while (i < start_delay) {
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
    while (true) {
      while (avg < base_weight + bin_weight / 2 && avg < -bin_weight / 2) {
        //Serial.println(avg, 3);
        take_reading();
        last_readings[counter % num_readings] = reading;
        last_avgs[counter % num_avgs] = avg;
        counter++;
      }
      for (int i = 0; i < 100; i++) {
        take_reading();
        last_readings[counter % num_readings] = reading;
        last_avgs[counter % num_avgs] = avg;
        counter++;
      }
      if (avg > base_weight + bin_weight / 2 || avg > -bin_weight / 2) {
        break;
      }
    }
    reset_scale();
  }
}

void occasional_checks() {
  // stuff to check every check_freq minutes
  if (millis() - last_check >= check_interval) {
    // check to see if we need to premptively need to start recording data from the other scales
    if(!minor_scale_setup){
      last_check += 2000;
      minor_scale_setup = true;
    }
    else {
      // Camera's Scale
      Serial.println("weight 1 checked");
      Serial.println(avg, 3);
  
      // Other Scales (Middle and Far)
      Serial.println("weight 2 checked");
      Serial.println(sum_trash/num_minor_scale_measure, 3);
      
      Serial.println("weight 3 checked");
      Serial.println(sum_far/num_minor_scale_measure,3);

      // reset the vars used for printing the minor scales weight
      sum_trash = 0;
      sum_far = 0;
      num_minor_scale_measure = 0;
      minor_scale_setup = false;

      
      // Stuff to make sure that this can continue working
      last_check += check_interval;
      max_weight[0] = max_weight[1];
      max_weight[1] = avg;
      //String input = Serial.readString();
      //Serial.println(input);
      if (Serial.readString() == "zero scales") {
        zero_scales();
      }
    }
  }
}

void setup() {
  Serial.begin(9600);

  pinMode(9,OUTPUT);
  digitalWrite(9,HIGH);     // This is so that we can have other ports as 5V for the other
  pinMode(10,OUTPUT);       // scales.
  digitalWrite(10 ,HIGH);  

  scale_trash.begin(DOUT_MIDDLE, CLK_MIDDLE);
  scale_trash.set_scale(calibration_factor_2); //This value is obtained by using the SparkFun_HX711_Calibration sketch

  scale_far.begin(DOUT_FAR, CLK_FAR);
  scale_far.set_scale(calibration_factor_3); //This value is obtained by using the SparkFun_HX711_Calibration sketch

  scale.begin(DOUT_CAM, CLK_CAM);
  scale.set_scale(calibration_factor_1); //This value is obtained by using the SparkFun_HX711_Calibration sketch
  
  zero_scales();

}

void loop() {

//  Serial.println("made it here");
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
