import os
import time
import shutil

pic_dir = 'C:/Users/Ben/Code/GarbageGraderData/RPiPics'

import fastai.vision as favi
import torch
import os
import random
import shutil
import time

os.system('start current_pic.jpg')
os.system('start current_grade.jpg')

def grade(test_image):
  img = favi.open_image(test_image)
  pred_class, pred_idx, outputs = learn.predict(img)
  print("\nPrediction:", pred_class)
  print("\nProbabilities:")
  probs = sorted([[classes[i], round(float(outputs[i]), 2)] for i in range(6)],
                                key = lambda x: x[1], reverse = True)
  for letter, prob in probs:
      print("%s: %.2f" % (letter, prob))
  return pred_class

learn = favi.load_learner('Production-Model')

classes = 'ABCDFN'

def check_and_grade():
    while True:
        try:
            if os.scandir(pic_dir + '/incoming'):
                for pic in os.scandir(pic_dir + '/incoming'):
                    print('\n' + pic.name)
                    while True:
                        try:
                            current_grade = grade(pic.path)
                            shutil.copy(pic.path, 'current_pic.jpg')
                            shutil.copy(str.format('grade_pics/%s.jpg' % current_grade),
                                        'current_grade.jpg')
                            shutil.move(pic.path, pic_dir + '/archived/' + pic.name)
                            break
                        except PermissionError:
                            continue
        except OSError:
            break
    print("\n[BROKEN IMAGE]")
    shutil.move(pic.path, pic_dir + '/archived/' + pic.name)
    return

while True:
    check_and_grade()
