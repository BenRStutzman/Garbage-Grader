#----------------------------------------------------------------------#
# Importing packages

import csv, random, sys, os, shutil, time

#----------------------------------------------------------------------#
# Convenience Methods

# Code that can be run by entering n as a parameter on commandline
def setup_csv(folder_name, grades_file):
    # will break if you use fewer than 30 total pictures
    print("Setting up gradebook... thank you for your patience.")
    for file in os.scandir(folder_name):
        if len(file.name) == 11:
            os.remove(file.path)
    for file in random.sample(list(os.scandir(folder_name)), 30):
        new_name = '1' + file.name
        shutil.copy(file.path, folder_name + '\\' + new_name)
    index = []
    for pic in os.scandir(folder_name):                  # since pic numbers won't necessarily start at 0 and be consecutive.
        index.append([int(pic.name.split('.')[0])])
    write_csv(grades_file, index)

# code that writes a 2-d dictionary to a csv file
def write_csv(fp,data):
    with open(fp, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerows(data)


# find the name of the folder full of pictures (assuming it's the only folder in the current directory)
def find_folder_name():
    for item in os.scandir():
        if item.is_dir() and item.name.startswith("Set_"):
            return item.name
    else:
        return False

def early_quit(grades_file, pic_list):
    write_csv(grades_file, pic_list)
    pics_to_grade = len([pic for pic in pic_list if len(pic) == 1]) # checks how many pictures have not yet been graded
    print('\nYou have %d pictures left to grade in this set.' % pics_to_grade)
    print('Exiting grader, progress saved.')

#----------------------------------------------------------------------#
# Variable declarations

last_pic = 'placeholder.jpg'
pic_list = []
params = sys.argv

#----------------------------------------------------------------------#
# Main function

auto_local = False
flash_drive = False if auto_local or 'local' in params else True

if flash_drive:
    for letter in ['D','E','F','G']:
        try:
            dir = letter + ':\\Other'
            os.chdir(dir)
            folder_name = find_folder_name()
            print('Running from USB in drive ' + letter)
            break
        except FileNotFoundError:
            continue
        except PermissionError:
            continue
else:
    dir = 'C:\\GRADER0\\Other'
    os.chdir(dir)
    folder_name = find_folder_name()
    print('Running locally from C:\\GRADER0')

if not folder_name:
    print('Make sure the folder of pictures to grade is in this directory')
    raise Exception

grades_file = folder_name[:-4] + "_grades.csv" #automatic name for the grades csv

if 'clear' in params:
    if input('Are you sure you want to overwrite the grades file (y/n)? ') == 'y':
        setup_csv(folder_name, grades_file)
        print('erasing current grades file...')
        time.sleep(1)
    else:
        print('keeping current grades file...')
        time.sleep(1)

# This is creating a list of the rows of the csv for ease of reading and writing without constantly reading and writing to the file.
try:
    csv_file = open(grades_file)
except FileNotFoundError:

    setup_csv(folder_name, grades_file)
    csv_file = open(grades_file)

csv_reader = csv.reader(csv_file, delimiter=',')
line_count = 0
for row in csv_reader:
    pic_list.append(row)
csv_file.close()

pics_to_grade = len([pic for pic in pic_list if len(pic) == 1]) # checks how many pictures have not yet been graded

if pics_to_grade:

    print("\nWelcome to the Garbage Grader! Drag this window and the "
            "picture-viewing window to a convenient place, then press "
            "enter to begin grading.")
    time.sleep(2)
    shutil.copy('placeholder.jpg', 'current_pic.jpg')
    os.system('start ' + dir + '\\JPEGView64\\JPEGView current_pic.jpg')  # opens current_pic.jpg in the default photo viewer
    input()                             # waits for the user to press enter

    print("You have %d pictures left to grade in this set... Let's begin!\n"
          "\nAt any time, you may enter:\n'<' to go back to the previous picture\n"
          "'#' to see how many pictures are left\n'q' to save your progress"
          " and quit\n" % pics_to_grade)
    time.sleep(1)

    # This sets up the random sample with no repeats of the picture that we want to pull from all numbers will have 1 added as the 0th picture doesn't matter in this case, and the last picture does.
    sample = [pic_num for pic_num in random.sample(range(len(pic_list)),len(pic_list)) if len(pic_list[pic_num]) == 1]

    # Iterating through each of the pictures in the list. Copies the pictures into current_pic.jpg and then takes in the grade of commandline. Can break out with Ctrl c.
    go_back = False
    i = 0
    max_i = 0
    while i < len(sample):
        sample_num = sample[i]
        id = int(pic_list[sample_num][0])
        if len(pic_list[sample_num]) == 1 or i < max_i: #if it still needs a grade
            max_i = max(i, max_i)
            try:
                id_str = format(id, '06d')

                file_path = folder_name + '\\' + id_str + '.jpg'

                shutil.copy(file_path, 'current_pic.jpg') #copy the picture into current_pic.jpg, which is already pulled up in the default photo viewer

                grade = input("What grade would you give this picture (%s.jpg)?\n" % id_str).strip().upper()

                while grade in ['#', '']:
                    if grade == '#':
                        pics_to_grade = len([pic for pic in pic_list if len(pic) == 1]) # checks how many pictures have not yet been graded
                        print('\nYou have %d pictures left to grade in this set.' % pics_to_grade)
                    else:
                        print("Whoops, I didn't catch that.")
                    grade = input("\nWhat grade would you give this picture (%s.jpg)?\n" % id_str).strip().upper()

                if grade == 'Q': # quit
                    raise KeyboardInterrupt

                if grade == '<': # go back to last picture
                    i -= 1
                    continue

                if len(pic_list[sample_num]) == 1:
                    pic_list[sample_num].append(grade)
                else:
                    pic_list[sample_num][1] = grade

            except Exception as e:
                print(e)
                print("Make sure you aren't grading too quickly...") # the try sometimes throws an error if I grade really fast
                early_quit(grades_file, pic_list)
                break
            except KeyboardInterrupt:
                early_quit(grades_file, pic_list)
                break
        write_csv(grades_file, pic_list)
        i += 1
    else:
        # writes to the csv file
        write_csv(grades_file, pic_list)
        shutil.copy('placeholder.jpg', 'current_pic.jpg')
        print('\nDone grading! Please return this flash drive to Austin or Ben ASAP.')
else:
    print('There are no pictures left to grade in this set. Please return this '
          'flash drive to Ben or Austin ASAP.')

time.sleep(3)
os.system('taskkill /IM JPEGView.exe /f > nul')
