#----------------------------------------------------------------------#
# Importing packages

import csv, random, sys, os
from PIL import Image

#----------------------------------------------------------------------#
# Convenience Methods

# Code that can be run by entering n as a parameter on commandline
def setup_csv(suffix,size):
    index = []
    for i in range(size):
        index.append([i])
    write_csv("grades\\" + str(suffix), index)

# code that writes a 2-d dictionary to a csv file
def write_csv(fp,data):
    with open(fp, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerows(data)

#----------------------------------------------------------------------#
# Variable declarations

pic_list = []
params = sys.argv

#----------------------------------------------------------------------#
# Main function

# checks to see if csv needs setup
try:
    if (params[1] == 'n'):
        setup_csv(input("What should the filename be?\n"),input("How many rows?\n"))
except:
    pass


# This is creating a list of the rows of the csv for ease of reading and writing without constantly reading and writing to the file.
with open(r'.\grades\1123-1201') as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=',')
    line_count = 0
    for row in csv_reader:
        pic_list.append(row)


# This sets up the random sample with no repeats of the picture that we want to pull from all numbers will have 1 added as the 0th picture doesn't matter in this case, and the last picture does.
sample = random.sample(range(1227),1227)

# Iterating through each of the pictures in the list. Pulls up the picture and then takes in the grade of commandline. Can break out with Ctrl c.
for id in sample:
    try:
        id_str = format(id, '06d')
        file_path = "start ..\\..\\Data\\11-23_to_12-1\\composites\\food\\" + id_str + ".jpg"
        os.system(file_path)

        grade = input("What grade would you give the picture " + id_str + "?\n")

        pic_list[id].append(grade)
    except Exception as e:
        break


# writes to the csv file
write_csv(r'.\grades\1123-1201',pic_list)
