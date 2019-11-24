from PIL import Image
import os
import datetime
import serial
import time

def save_composite(buffer_size = 4, inp_folder = "photostream",
                    out_folder = "composites", ident = 0):

    buffer = []
    for file in os.scandir(inp_folder):
        if file.path[-1] != '~': # make sure it's not a hidden file
            buffer.append(file.path)

    paths = sorted(buffer, key = lambda path: int(path[len(inp_folder) + 1 : -4]))[-buffer_size:]
    pictures = []
    for path in paths:
        pictures.append(Image.open(path))

    # following 10ish lines are from glombard on github:
    # https://gist.github.com/glombard/7cd166e311992a828675
    
    composite = Image.new("RGB", (5184, 3888))

    for index, picture in enumerate(pictures):
      #picture.thumbnail((2592, 900), Image.ANTIALIAS)
      x = index % 2 * 2592
      y = index // 2 * 1944
      w, h = picture .size
      #print('pos {0},{1} size {2},{3}'.format(x, y, w, h))
      composite.paste(picture, (x, y, x + w, y + h))

    composite.save(os.path.expanduser('%s/%d.jpg' % (out_folder, ident)))
    composite.close()

def nice_date_time(year, month, day, hour, minute, second):
    return str.format("%d-%.2d-%.2d %.2d:%.2d:%.2d" % (year, month, day, hour,
                                                        minute, second))

if input("WARNING: this will overwrite the current folder of composites. Enter "
         "'y' to continue or any other key to quit: ") == 'y':

    out_folder = 'composites'
    os.system("rm %s/*" % out_folder)

    serial_port = '/dev/ttyACM0';
    baud_rate = 9600; #In arduino, Serial.begin(baud_rate)
    path = "Data/Scale Data/sample.csv";

    f = open(path, 'w');
    ser = serial.Serial(serial_port, baud_rate)
    ser.reset_input_buffer()
    print("Initializing...")
    ard_output = ser.readline().decode('utf-8').strip()
    print("Release the crackers!", end = "\n\n")

    header = "Time,Addition ID,Trigger,Weight (g)"
    print(header)
    f.write(header + "\n")
    start = datetime.datetime.now()
    start_date = nice_date_time(start.year, start.month, start.day,
                                             start.hour, start.minute, start.second)
    line = start_date +  ",0," + ard_output
    print(line)
    f.write(line + "\n")
    ident = 0

    while True:
        f = open(path, 'a')
        ard_output = ser.readline().decode('utf-8').strip()
        if ard_output == "food added":
            ident += 1
            save_composite(ident = ident)
        now = datetime.datetime.now()
        info = nice_date_time(now.year, now.month, now.day,
                              now.hour, now.minute, now.second)
        #info += str(round((now - start).total_seconds() / 3600, 4))
        info += "," + str(ident) + ","
        line = info + ard_output
        print(line)
        f.write(line+"\n")
        f.close()

