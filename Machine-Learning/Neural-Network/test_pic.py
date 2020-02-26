import os
import sys

dest_path = 'BenS@10.3.60.101:GarbageGrader/RPiPics/incoming/'

set_num, pic_num = [int(num) for num in sys.argv[1:3]]

pic_name = str.format('%06d.jpg' % pic_num)
set_name = 'Set_' + str(set_num)

pic_path = ('C:/Users/Ben/Code/GarbageGraderData/TrainingData/' + set_name +
    '/' + set_name + '_all/' + pic_name)

os.system('scp ' + pic_path + ' ' + dest_path + set_name + '_' + pic_name)
