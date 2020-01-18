from PIL import Image
import os
import serial
import datetime
import time
import sys

photostream = "/home/pi/GarbageGrader/Data/photostream"
food_folder = "/home/pi/GarbageGrader/Data/composites/food"
other_folder = "/home/pi/GarbageGrader/Data/composites/other"
log = "/home/pi/GarbageGrader/Data/log.csv"
on_hours = [6, 21]

def save_composite(ident, out_folder, num_tiles = 4, inp_folder = photostream):

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
    
    composite = Image.new("RGB", (3200, 3200))

    for index, picture in enumerate(reversed(pictures)):
        
        x = index % 2 * 1600
        y = index // 2 * 1600
      
        composite.paste(picture.crop((466, 0, 2066, 1600)),
                                    (x, y, x + 1600, y + 1600))

    composite.save(os.path.expanduser('%s/%06d.jpg' % (out_folder, ident)))
    composite.close()

def nice_date_time(year, month, day, hour, minute, second):
    return str.format("%d-%.2d-%.2d %.2d:%.2d:%.2d" % (year, month, day, hour,
                                                        minute, second))

def record_events(photo_folder, food_folder, other_folder, log, on_hours,
                  prev_id):

    now = datetime.datetime.now()
    ser = serial.Serial('/dev/ttyACM0', 9600)
    action = ''
    saved_action = ''
    day = True
    print("\nTime                  ID       Action           "
                  "Weight (kg)   Weight (g)")

    ident = prev_id
    while True:
        hours = now.hour + now.minute / 60
        if on_hours[0] < hours < on_hours[1]:
            if not day:
                day = True
                ser.reset_input_buffer()
                ser.write(bytes('reset scale 1', 'utf-8'))
                print("\nWaking up...")
                ard_output = ser.readline().decode('utf-8').strip() 
                print("\nTime                  ID       Action           "
                  "Weight (kg)   Weight (g)")
            else:
                ard_output = ser.readline().decode('utf-8').strip()
            if ard_output[0].isalpha():
                if action in ['food added', 'bin removed', 'scale reset']:
                    saved_action = action
                    saved_now = now
                action = ard_output
                if action in ['food added', 'bin removed', 'scale reset']:
                    ident += 1
                    out_folder = food_folder if action == 'food added' else other_folder
                    save_composite(ident, out_folder)
                now = datetime.datetime.now()
            elif action:
                if action in ['food added', 'bin removed', 'scale reset']:
                    to_save, to_print = formatter(now, action, ard_output, ident)
                else:
                    to_save, to_print = formatter(now, action, ard_output)
                action = ''
                log.write(to_save)
                log.flush()
                print(to_print)
            elif saved_action:
                to_save, to_print = formatter(saved_now, saved_action, ard_output, ident)
                saved_action = ''
                log.write(to_save)
                log.flush()
                print(to_print)
            else:
                print('There was no action or saved action, but I got a number.')
        else:
            if day:
                day = False
                if action in ['food added', 'bin removed', 'scale reset']:
                    out_folder = food_folder if action == 'food added' else other_folder
                    pic_path = str.format('%s/%06d.jpg' % (out_folder, ident))
                    os.remove(pic_path)
                    ident -= 1
                action = ''
                print("\nGoing to sleep...")
            time.sleep(60)

def formatter(now, action, weight, ident = -1):
    info = nice_date_time(now.year, now.month, now.day,
                          now.hour, now.minute, now.second)
    if action == 'food added':
        weight1, weight2 = "", weight
    else:
        weight1, weight2 = weight, ""
    if ident == -1:
        id_str = ""
    else:
        id_str = str.format("%06d" % ident)
    to_save = str.format("%s,%s,%s,%s,%s\n" %
                         (info, id_str, action, weight1, weight2))
    to_print = str.format("%s   %6s   %s   %8s      %8s" %
                         (info, id_str, str.ljust(action, 14),
                          weight1, weight2))
    return to_save, to_print

def log_pics_and_weights(clear_logs, in_folder = photostream,
                         food_folder = food_folder, other_folder = other_folder,
                         path = log, on_hours = on_hours):

    header = "Time,ID,Action,Weight (kg),Weight (g)"
    if clear_logs:
        if input("Are you sure you want to clear the log and delete all pictures"
                 " (y/n)? ") != 'y':
            print("Canceling...")
            return
        prev_id = -1
        for pic in os.scandir(food_folder):
            os.remove(pic)
        for pic in os.scandir(other_folder):
            os.remove(pic)
        f = open(path, 'w')
        f.write(header + '\n')
    else:
        max_id = -1
        f = open(path, 'r')
        lines = f.readlines()
        for line in reversed(lines):
            try:
                prev_id = int(line.split(',')[1])
                break
            except ValueError:
                continue
        else:
            prev_id = -1
    f.close()

    f = open(path, 'a')
    
    record_events(in_folder, food_folder, other_folder, f, on_hours, prev_id)


if len(sys.argv) > 1 and sys.argv[1] == 'clear':
    clear_logs = True
else:
    clear_logs = False

log_pics_and_weights(clear_logs)

