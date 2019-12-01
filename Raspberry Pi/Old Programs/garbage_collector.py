import os
import time

while True:
    files = sorted([f.path for f in os.scandir('photostream')])
    for file in files[:-10]:
        os.remove(file)
    time.sleep(1)
    
