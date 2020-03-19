import datetime
import os
import sys

on_time = 7
off_time = 20

params = sys.argv
if len(params) > 1:
    if params[1] == 'today':
        os.system('echo on 0 | cec-client -s -d 1')
        while datetime.datetime.now().hour < off_time:
            continue
        os.system('echo standby 0 | cec-client -s -d 1')

while True:
    while datetime.datetime.now().hour != 0:
        continue
    while datetime.datetime.now().hour < on_time:
        continue
    os.system('echo on 0 | cec-client -s -d 1')
    while datetime.datetime.now().hour < off_time:
        continue
    os.system('echo standby 0 | cec-client -s -d 1')
    
