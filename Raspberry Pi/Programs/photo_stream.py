import os
import serial
import time
import threading
import datetime
import time

photostream = "/home/pi/GarbageGrader/Data/photostream"

on_hours = [6, 21]

def stream_photos(folder = photostream, filename = "", shutter = 10000,
                  ISO = None, brightness = None, contrast = None,
                  on_hours = on_hours):

    shutter_str = " -ss " + str(shutter)
    ISO_str = "" if ISO == None else " -ISO " + str(ISO)
    brightness_str = "" if brightness == None else " -br " + str(brightness)
    contrast_str = "" if contrast == None else " -co " + str(contrast)
    path = folder + "/" + filename

    day = False
    batch = 0

    while True:
        now = datetime.datetime.now()
        hours = now.hour + now.minute / 60
        if on_hours[0] - 0.25 < hours < on_hours[1] + 0.25:
            if not day:
                day = True
                for pic in os.scandir(folder):
                    try:
                        os.remove(pic)
                    except:
                        pass
                batch = 0
            if os.system("raspistill -t 60000 -tl 0 -o %s%03d%%03d.jpg%s%s%s%s"
              % (path, batch, shutter_str, ISO_str, brightness_str, contrast_str)):
                break
            batch += 1
        else:
            if day:
                day = False
            time.sleep(60)



def collect_garbage(num_to_leave = 10, folder = photostream, on_hours = on_hours):

    while True:
        now = datetime.datetime.now()
        hours = now.hour + now.minute / 60
        if on_hours[0] - 0.5 < hours < on_hours[1] + 0.5:
            files = sorted([f.path for f in os.scandir(folder)])
            for file in files[:-num_to_leave]:
                try:
                    os.remove(file)
                except:
                    pass
            time.sleep(1)
        else:
            time.sleep(60)


streamer = threading.Thread(target = stream_photos, kwargs = {})
collector = threading.Thread(target = collect_garbage, kwargs = {})

streamer.start()
collector.start()
