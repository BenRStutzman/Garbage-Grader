pic_dir = '/home/BenS/GarbageGrader/RPiPics/'
server_dir = ('/home/BenS/GarbageGrader/django-webserver/mysite/'
	'GarbageDisplay/static/pictures/')
log_path = '/home/BenS/GarbageGrader/NeuralNet/log.csv'

import fastai.vision as favi
import torch
import os
import random
import shutil
import datetime

#os.system('start current_pic.jpg')
#os.system('start current_grade.jpg')

def grade_image(test_image):
	img = favi.open_image(test_image)
	pred_class, pred_idx, outputs = learn.predict(img)
	return pred_class, outputs

def check_and_grade():
	while True:
		if os.scandir(pic_dir + 'incoming'):
			for pic in os.scandir(pic_dir + 'incoming'):
				print('_' * 80 + '\n\n' + pic.name, end = '\n\n')
				while True:
					try:
						now = datetime.datetime.now()
						grade, probs = grade_image(pic.path)
						shutil.copy(pic.path, server_dir + pic.name)

						# SEND STUFF TO DATABASE
						# Picture name: pic.name (includes .jpg)
						# Grade: grade
		 				# Timestamp: now

						# ---Everything below this line is not needed for the webserver---

						# Printing to console

						for i, letter in enumerate('ABCDFN'):
							print(letter, end = ' |')
							print(int(probs[i] * 50) * '*')

						print('\nGrade:', grade)

						# Archiving the picture (separate from copying to static folder)

						shutil.move(pic.path, pic_dir + 'processed/' + pic.name)

						# Logging the time, picture name, grade, and probabilites

						nice_time = str.format('%04d-%02d-%02d %02d:%02d:%02d' % (now.year,
							now.month, now.day, now.hour, now.minute, now.second))

						nice_probs = [str.format('%.2f' % float(prob)) for prob in probs]

						log_line = str.format('%s,%s,%s,%s\n' % (nice_time,
							pic.name.split('.')[0], grade, ','.join(nice_probs)))

						with open(log_path, 'a') as log:
							log.write(log_line)

						break

					except PermissionError:
						print("PermissionError!!!")
						continue

					except OSError: #this will probably occur about 20 times before the picture is fully received.
						# print("OSError ;)")
						continue

os.system('touch ' + log_path)

learn = favi.load_learner(prog_dir + 'Production-Model')

while True:
    check_and_grade()
