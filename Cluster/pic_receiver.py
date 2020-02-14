import os
import time
import shutil

base_dir = 'C:/Users/Ben/Code/GarbageGraderData/RPiPics'

while True:
    if os.scandir(base_dir + '/incoming'):
        for pic in os.scandir(base_dir + '/incoming'):
            print(pic.name)
            while True:
                try:
                    shutil.copy(pic.path, base_dir + '/current_pic.jpg')
                    shutil.move(pic.path, base_dir + '/archived/' + pic.name)
                    break
                except PermissionError:
                    continue
