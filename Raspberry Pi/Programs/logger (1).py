from PIL import Image
import os
import serial
import datetime
import time
import sys

photostream = "/home/pi/GarbageGrader/Data/photostream"
food_folder = "/home/pi/GarbageGrader/Data/composites/food"
other_folder = "/home/pi/GarbageGrader/Data/composites/other"
dest_folder = 'Ben@10.6.21.20:C:/Users/Ben/Code/GarbageGraderData/RPiPics/Incoming'
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
    pic_path = str.format('%s/%06d.jpg' % (out_folder, ident))

    composite.save(pic_path)
    if out_folder == food_folder:
        os.system('scp ' + pic_path + ' ' + dest_folder); #send to cluster
    composite.close()

def nice_date_time(year, month, day, hour, minute, second):
    return str.format("%d-%.2d-%.2d %.2d:%.2d:%.2d" % (year, month, day, hour,
                                                        minute, second))

def nice_time(hour, minute, second):
    return str.format("%.2d:%.2d:%.2d" % (hour, minute, second))

def record_events(photo_folder, food_folder, other_folder, log, on_hours,
                  prev_id):
    weight_queue = [-1, -1, -1]
    while True:
        try:
            ser = serial.Serial('/dev/ttyACM0', 9600)
            break
        except serial.serialutil.SerialException:
            print("Arduino not detected. Trying again in 5 minutes...")
            time.sleep(300)
            
    action = ''
    saved_action = ''
    cur_time = datetime.datetime.now()
    hours = cur_time.hour + cur_time.minute / 60
    if on_hours[0] < hours < on_hours[1]: # if starting at night
        night_start = False
    else:
        night_start = True
    day = True
    terminal_header = "\nTime      ID      Action          Item (g)   Wt1 (kg)   Wt2 (kg)   Wt3 (kg)"
    print(terminal_header)

    ident = prev_id
    while True:
        cur_time = datetime.datetime.now()
        hours = cur_time.hour + cur_time.minute / 60
        if on_hours[0] < hours < on_hours[1]: # if during "daytime":
            if not day: # wake up sequence
                day = True
                ser.reset_input_buffer()
                ser.write(bytes('zero scales', 'utf-8'))
                print("\nWaking up...")
                ard_output = ser.readline().decode('utf-8').strip()
                print(terminal_header)
            else: # already awake
                ard_output = ser.readline().decode('utf-8').strip()

            if ard_output[0].isalpha(): # action from the arduino
                # if already action waiting, stow it for later till it gets its number
                if action in ['food added', 'bin removed', 'scale reset', 'scales reset']:
                    saved_action = action
                    saved_now = now
                action = ard_output # save the action to wait for its number
                if action in ['food added', 'bin removed', 'scale reset', 'scales reset']:
                    ident += 1
                    out_folder = food_folder if action == 'food added' else other_folder
                    save_composite(ident, out_folder) # save a picture
                now = datetime.datetime.now()
            else: # numerical Arduino output
                if action: # action waiting for number
                    if action == 'food added':
                        to_save, to_print = formatter(now, action,
                                        item_weight = ard_output, ident = ident)
                    elif action in ['bin removed', 'scale reset']:
                        to_save, to_print = formatter(now, action,
                                            weight1 = ard_output, ident = ident)
                    elif action == 'scales reset':
                        to_save, to_print = formatter(now, action,
                                weight1 = ard_output, weight2 = '0.000',
                                weight3 = '0.000', ident = ident)
                    elif action == 'weight 1 checked':
                        weight_queue[0] = ard_output
                        action = ''
                        continue
                    elif action == 'weight 2 checked':
                        weight_queue[1] = ard_output
                        action = ''
                        continue
                    elif action == 'weight 3 checked':
                        weight_queue[2] = ard_output
                        to_save, to_print = formatter(now, 'weight checked', weight1 = weight_queue[0],
                                            weight2 = weight_queue[1], weight3 = weight_queue[2])
                        weight_queue = [-1, -1, -1]
                    action = ''
                    log.write(to_save)
                    log.flush()
                    print(to_print)
                elif saved_action: # saved action waiting for a number
                    if saved_action == 'food added':
                        to_save, to_print = formatter(saved_now, saved_action,
                                        item_weight = ard_output, ident = ident)
                    elif saved_action == 'scales reset':
                        to_save, to_print = formatter(saved_now, saved_action,
                                        weight1 = ard_output, weight2 = '0.000',
                                        weight3 = '0.000', ident = ident)
                    else: # bin removal or scale reset saved
                        to_save, to_print = formatter(saved_now, saved_action,
                                            weight1 = ard_output, ident = ident)
                    saved_action = ''
                    log.write(to_save)
                    log.flush()
                    print(to_print)
                else:
                    print('There was no action or saved action, but I got a number.')
        else: # not during "daytime" hours
            if day: # go-to-sleep sequence
                day = False
                # leftover picture; delete it and decrement ID
                if action in ['food added', 'bin removed', 'scale reset', 'scales reset']:
                    out_folder = food_folder if action == 'food added' else other_folder
                    pic_path = str.format('%s/%06d.jpg' % (out_folder, ident))
                    try:
                        os.remove(pic_path)
                    except:
                        pass
                    ident -= 1
                action = '' # clear the actions and queues
                saved_action = ''
                weight_queue = [-1, -1, -1]
                print("\nGoing to sleep...")
                # if it's been on for the day and is now turning off, restart Pi
                if not night_start:
                    time.sleep(10)
                    os.system("sudo reboot")
                night_start = False
            # already asleep
            time.sleep(60)

def formatter(now, action, item_weight = '', weight1 = '', weight2 = '', weight3 = '', ident = -1):
    nice_dt = nice_date_time(now.year, now.month, now.day,
                          now.hour, now.minute, now.second)
    nice_t = nice_time(now.hour, now.minute, now.second)
    if ident == -1:
        id_str = ""
    else:
        id_str = str.format("%06d" % ident)
    to_save = str.format("%s,%s,%s,%s,%s,%s,%s\n" %
                         (nice_dt, id_str, action, item_weight, weight1, weight2, weight3))
    to_print = str.format("%s  %6s  %s%8s  %8s   %8s   %8s" %
                         (nice_t, id_str, str.ljust(action, 14),
                          item_weight, weight1, weight2, weight3))
    return to_save, to_print

def log_pics_and_weights(clear_logs, in_folder = photostream,
                         food_folder = food_folder, other_folder = other_folder,
                         path = log, on_hours = on_hours):

    header = "Time,ID,Action,Item weight (g),Weight 1 (kg),Weight 2 (kg),Weight 3 (kg)"
    if clear_logs:
        if input("Are you sure you want to clear the log and delete all pictures"
                 " (y/n)? ") != 'y':
            print("Canceling...")
            return
        prev_id = -1
        for pic in os.scandir(food_folder):
            try:
                os.remove(pic)
            except:
                pass
        for pic in os.scandir(other_folder):
            try:
                os.remove(pic)
            except:
                pass
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
