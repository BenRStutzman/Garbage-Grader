import os
import time

source_folder = '/home/pi/GarbageGrader/Data/photostream
dest_folder = 'Ben@10.6.21.20:C:/Users/Ben/Code/GarbageGraderData/RPiPics/incoming_frames'
delete_afterward = False

while True:
    for pic in os.scandir(photo_stream):
        if os.system('scp ' + pic.path + ' ' + dest_folder):
            print("couldn't send; sleeping for 10 mins...")
            time.sleep(600)
        elif delete_afterward:
            os.remove(pic.path)
