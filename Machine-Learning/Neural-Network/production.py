root_dir = "C:/Users/Ben/Code/"
model_dir = root_dir + "GarbageGrader/Machine-Learning/Neural-Network/Production-Model/"
pic_dir = root_dir + "GarbageGraderData/Training Data/"

import fastai.vision as favi
import torch
import os
import random
import shutil
import time

classes = 'ABCDFN'

test_image_set = 14

def grade_random():
    if graded:
      test_class = random.choice(classes)
      test_image = random.choice(lists_of_pics[test_class])
    else:
      test_image = random.choice(list_of_pics)
    grade(test_image.path)


def grade(test_image):
  shutil.copy(test_image, 'current_image.jpg')
  img = favi.open_image(test_image)
  print('\nSet %d: %s' % (test_image_set, test_image.split('\\')[-1]))
  pred_class, pred_idx, outputs = learn.predict(img)
  print("\nPrediction:", pred_class)
  if graded:
    print('Actual:', test_class)
    pred_class = str(pred_class)
    if pred_class == test_class:
      print("[Correct]")
    elif pred_class == 'N' or test_class == 'N':
      print("[Incorrect]")
    elif abs(classes.index(pred_class) - classes.index(test_class)) == 1:
      print("[Incorrect, but close]")
    else:
      print("[Incorrect]")
  print("\nProbabilities:")
  probs = sorted([[classes[i], round(float(outputs[i]), 2)] for i in range(6)],
                                key = lambda x: x[1], reverse = True)
  for letter, prob in probs:
      print("%s: %.2f" % (letter, prob))

try:
  lists_of_pics = {grade: list(os.scandir(pic_dir + "Set_" + str(test_image_set) + "/Set_" + str(test_image_set) + "_sorted/" + grade)) for grade in 'ABCDFN'}
  graded = True
except FileNotFoundError:
  list_of_pics = list(os.scandir(pic_dir + "Set_" + str(test_image_set) + "/Set_" + str(test_image_set) + "_all"))
  graded = False

learn = favi.load_learner(model_dir)

os.system('start JPEGView64\\JPEGView current_pic.jpg')

while True:
    response = input("\nEnter a picture number, or just press enter to "
                     "grade a random picture: ")
    if response == 'q':
        break
    elif response:
        try:
            test_image = str.format('%s/Set_%d/Set_%d_all/%06d.jpg'
                % (pic_dir, test_image_set, test_image_set, int(response)))
            grade(test_image)
        except FileNotFoundError:
            print("\nImage %s not found in Set %d" % (response, test_image_set))
    else:
        grade_random()

time.sleep(3)
os.system('taskkill /IM JPEGView.exe /f > nul')
