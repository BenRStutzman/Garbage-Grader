import time
import datetime
import os
ping_log = '/home/pi/GarbageGrader/Data/ping_log.txt'

while True:
    with open(ping_log, 'a') as f:
        f.write('\n' + str(datetime.datetime.now()) + '\n')
    os.system('ping -c 1 10.6.10.12 >> ' + ping_log)
    time.sleep(600)
