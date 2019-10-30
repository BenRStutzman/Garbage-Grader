##############
## Script listens to serial port and writes contents into a file
##############
## requires pySerial to be installed 
import serial
import time

serial_port = '/dev/ttyACM0';
baud_rate = 9600; #In arduino, Serial.begin(baud_rate)
write_to_file_path = "Data/Scale Data/sample.csv";

output_file = open(write_to_file_path, "w+");
ser = serial.Serial(serial_port, baud_rate)
time.sleep(10)
line = ser.readline();
line = line.decode("utf-8").strip()
print(line)
output_file.write(line+"\n")
while True:
    line = ser.readline();
    line = line.decode("utf-8").strip() #ser.readline returns a binary, convert to string
    now = time.localtime()
    days = round(now.tm_yday + (now.tm_hour / 24) + (now.tm_min / 1440) + (now.tm_sec / 86400), 6)
    line = str(days) + "," + line
    print(line);
    output_file.write(line+"\n");
