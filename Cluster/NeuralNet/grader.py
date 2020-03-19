pic_dir = '/home/BenS/GarbageGrader/RPiPics/'
server_dir = ('/home/BenS/GarbageGrader/django-webserver/mysite/'
	'GarbageDisplay/static/pictures/')
model_dir = ('/home/BenS/GarbageGrader/NeuralNet/Production-Models/')
log_path = ('/home/BenS/GarbageGrader/NeuralNet/log.csv')

model_name = 'Sets_1-8_session-C.pkl' #The Neural Network, placed in model_dir

import sys
import fastai.vision as favi
import torch
import os
import shutil

sys.path.append("/home/BenS/GarbageGrader/django-webserver/mysite/")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mysite.settings")

import django
from django.utils import timezone

django.setup()

from GarbageDisplay.models import Picture


def grade_image(test_image):
	img = favi.open_image(test_image)
	pred_class, pred_idx, outputs = learn.predict(img)
	return str(pred_class), outputs

def check_and_grade():
	while True:
		if os.scandir(pic_dir + 'incoming'):
			for pic in os.scandir(pic_dir + 'incoming'):
				print('_' * 80 + '\n\n' + pic.name, end = '\n\n')
				while True:
					try:

						now = timezone.localtime(timezone.now())
						grade, probs = grade_image(pic.path)


						# only send non-'N' grades to the webserver
						if str(grade) != 'N':
							shutil.copy(pic.path, server_dir + pic.name)
							pic_to_db = Picture(name = pic.name,grade = grade, weight = 0, timestamp = now)
							pic_to_db.save()

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

					except OSError: #this will probably occur about 20 times before the picture is fully received.
						# print("OSError ;)")
						continue

os.system('touch ' + log_path)

learn = favi.load_learner(model_dir, file = model_name)

while True:
    check_and_grade()
