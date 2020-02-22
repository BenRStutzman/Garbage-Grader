pic_dir = '/home/BenS/GarbageGrader/RPiPics/'
prog_dir = '/home/BenS/GarbageGrader/NeuralNet/'
log_path = prog_dir + 'log.csv'

import fastai.vision as favi
import torch
import os
import random
import shutil
import time
import datetime

#os.system('start current_pic.jpg')
#os.system('start current_grade.jpg')

def grade(test_image):
  img = favi.open_image(test_image)
  pred_class, pred_idx, outputs = learn.predict(img)
  return pred_class, outputs

def check_and_grade():
    while True:
        try:
            if os.scandir(pic_dir + 'incoming'):
                for pic in os.scandir(pic_dir + 'incoming'):
                    print('\n' + pic.name)
                    time.sleep(0.1)
                    while True:
                        try:
                            current_grade, outputs = grade(pic.path)
                            shutil.copy(pic.path, prog_dir + 'current_pic.jpg')
                            shutil.copy(str.format('%sgrade_pics/%s.jpg' % (prog_dir, current_grade)), prog_dir + 'current_grade.jpg')

                            now = datetime.datetime.now()
                            nice_time = str.format('%04d-%02d-%02d %02d:%02d:%02d' % (now.year, now.month, now.day, now.hour, now.minute, now.second))
                            log_line = str.format('%s,%s,%s,%s\n' % (nice_time, pic.name, current_grade, ','.join([str(round(float(prob), 2)) for prob in outputs])))
                            with open(log_path, 'a') as log:
                            	log.write(log_line)
                            print('\nPrediction:', current_grade)
                            probs = sorted([[classes[i], round(float(outputs[i]), 2)] for i in range(6)],
                                key = lambda x: x[1], reverse = True)
                            print('\nProbabilities:')
                            for letter, prob in probs:
                              print('%s: %.2f' % (letter, prob))

                            shutil.move(pic.path, pic_dir + '/archived/' + pic.name)
                            break
                        except PermissionError:
                            continue
        except OSError:
            break
    print("\n[BROKEN IMAGE]")
    shutil.move(pic.path, pic_dir + '/archived/' + pic.name)
    return

os.system('touch ' + log_path)

learn = favi.load_learner(prog_dir + 'Production-Model')

classes = 'ABCDFN'

while True:
    check_and_grade()
