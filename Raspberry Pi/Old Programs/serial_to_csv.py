##############
## Script listens to serial port and writes contents into a file
##############
## requires pySerial to be installed 
import serial
import datetime
start = datetime.datetime.now()

serial_port = '/dev/ttyACM0';
baud_rate = 9600; #In arduino, Serial.begin(baud_rate)
path = "Data/Scale Data/sample.csv";

f = open(path, 'w');
ser = serial.Serial(serial_port, baud_rate)
ser.reset_input_buffer()
line = "Time,Elapsed Time (h),Moving Average(kg),"
line += "Additions Recorded,Addition Weight (g)"
print(line)
f.write(line+"\n")
ser.readline()
i = 0
while True:
    if i == 10:
        f.close()
        f = open(path, 'a')
        i = 0
    now = datetime.datetime.now()
    line = str.format("%d-%.2d-%.2d %.2d:%.2d:%.2d," % (now.year, now.month, now.day,
                                             now.hour, now.minute, now.second))
    line += str(round((now - start).total_seconds() / 3600, 4))
    ard_output = ser.readline().decode("utf-8").strip() #ser.readline returns a binary, convert to string
    line += "," + ard_output
    print(line);
    f.write(line+"\n");
    i += 1
