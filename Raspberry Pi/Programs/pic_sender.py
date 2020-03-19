import os
import time

food_folder = '/home/pi/GarbageGrader/Data/composites/food'
dest_folder = 'Ben@10.6.21.20:C:/Users/Ben/Code/GarbageGraderData/RPiPics/Incoming'

if os.scandir(food_folder):
    prev_pic = sorted([pic.name for pic in os.scandir(food_folder)])[-1]
else:
    prev_pic = ''

while True:
    if os.scandir(food_folder):
        last_pic = sorted([pic.name for pic in os.scandir(food_folder)])[-1]
        if last_pic != prev_pic:
            if os.system('scp ' + food_folder + '/' + last_pic + ' ' + dest_folder):
                print("sleeping for 10 mins...")
                time.sleep(600)
                if os.scandir(food_folder):
                    prev_pic = sorted([pic.name for pic in os.scandir(food_folder)])[-1]
                else:
                    prev_pic = ''
            else:
                prev_pic = last_pic
                
