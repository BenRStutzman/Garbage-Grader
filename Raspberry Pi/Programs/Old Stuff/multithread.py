from threading import Thread
from PIL import Image
import os
import serial
import datetime
import time

photostream = "/home/pi/GarbageGrader/Data/photostream"
composites = "/home/pi/GarbageGrader/Data/composites"
log = "/home/pi/GarbageGrader/Data/log.csv"

def stream_photos(folder = photostream, filename = "", shutter = None,
                  ISO = None, brightness = None, contrast = None):

    if os.scandir(folder):
        os.system("rm %s/*" % folder)
    shutter_str = " -ss " + str(shutter)
    ISO_str = "" if ISO == None else " -ISO " + str(ISO)
    brightness_str = "" if brightness == None else " -br " + str(brightness)
    contrast_str = "" if contrast == None else " -co " + str(contrast)
    path = folder + "/" + filename

    os.system("raspistill -t 1000000000000 -tl 0 -o %s%%06d.jpg%s%s%s%s"
              % (path, shutter_str, ISO_str, brightness_str, contrast_str))


def collect_garbage(num_to_leave = 10, folder = photostream):
    while True:
        files = sorted([f.path for f in os.scandir(folder)])
        for file in files[:-num_to_leave]:
            os.remove(file)
        time.sleep(1)

def save_composite(ident = 0, num_tiles = 4, inp_folder = photostream,
                    out_folder = composites):

    buffer = []
    for file in os.scandir(inp_folder):
        if file.path[-1] != '~': # make sure it's not a hidden file
            buffer.append(file.path)

    paths = sorted(buffer, key = lambda path: int(path[len(inp_folder) + 1 : -4]),
                   reverse = True)
    pictures = []
    pic_num = 0
    while len(pictures) < num_tiles:
        try:
            pictures.append(Image.open(paths[pic_num]))
        except FileNotFoundError:
            continue
        finally:
            pic_num += 1


    # following 10ish lines are from glombard on github:
    # https://gist.github.com/glombard/7cd166e311992a828675
    
    composite = Image.new("RGB", (5184, 3888))

    for index, picture in enumerate(reversed(pictures)):
      #picture.thumbnail((2592, 900), Image.ANTIALIAS)
      x = index % 2 * 2592
      y = index // 2 * 1944
      w, h = picture .size
      #print('pos {0},{1} size {2},{3}'.format(x, y, w, h))
      composite.paste(picture, (x, y, x + w, y + h))

    composite.save(os.path.expanduser('%s/%06d.jpg' % (out_folder, ident)))
    composite.close()

def nice_date_time(year, month, day, hour, minute, second):
    return str.format("%d-%.2d-%.2d %.2d:%.2d:%.2d" % (year, month, day, hour,
                                                        minute, second))

def record_events(photo_folder, comp_folder, log, ser, starting_id = 1):

    ident = starting_id + 1
    while True:
        ard_output = ser.readline().decode('utf-8').strip()
        if ard_output == "food added":
            save_composite(ident = ident)
            now = datetime.datetime.now()
            info = nice_date_time(now.year, now.month, now.day,
                                  now.hour, now.minute, now.second)
            #info += str(round((now - start).total_seconds() / 3600, 4))
            info += str.format(",%06d," % ident)
            line = info + ard_output
        else:
            line += "," + ard_output
            log.write(line+"\n")
            log.flush()
            print(line.replace(",", "   "))
            ident += 1


def log_pics_and_weights(in_folder = photostream, out_folder = composites,
                         clear_logs = False, path = log, port = '/dev/ttyACM0'):

    header = "Time,ID,Action,Weight (g)"
    if clear_logs:
        starting_id = 0
        os.system("rm -r %s/*" % out_folder)
        f = open(path, 'w')
        f.write(header + '\n')
        f.close()
    else:
        max_id = -1
        f = open(path, 'r')
        lines = f.readlines()
        if len(lines) > 1:
            starting_id = int(lines[-1].split(',')[1]) + 1
        else:
            starting_id = 0
        f.close()

    f = open(path, 'a')

    ser = serial.Serial(port, 9600)
    ser.reset_input_buffer()
    print("Initializing...")
    ard_output = ser.readline().decode('utf-8').strip()
    print("Release the crackers!", end = "\n\n")

    
    print("       Time             ID       Action     Weight (g)")  
    save_composite(ident = starting_id)
    start = datetime.datetime.now()
    start_date = nice_date_time(start.year, start.month, start.day,
                                             start.hour, start.minute, start.second)
    line = str.format("%s,%06d,%s" % (start_date, starting_id, ard_output))
    f.write(line + "\n")
    f.flush()
    print(line.replace(',', '   '))
    

    record_events(in_folder, out_folder, f, ser, starting_id)

Thread(target = log_pics_and_weights, kwargs = {'clear_logs': True}).start()
Thread(target = stream_photos, kwargs = {'shutter': 10000}).start()
Thread(target = collect_garbage).start()

