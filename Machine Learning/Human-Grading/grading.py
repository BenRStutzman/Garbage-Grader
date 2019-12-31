#----------------------------------------------------------------------#
# Importing packages

import csv, random, sys, os, shutil, time

#----------------------------------------------------------------------#
# Convenience Methods

# Code that can be run by entering n as a parameter on commandline
def setup_csv(folder_name, grades_file):
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
        if item.is_dir() and item.name != '__pycache__':
            return item.name
    else:
        return False

def early_quit(grades_file, pic_list):
    write_csv(grades_file, pic_list)
    pics_to_grade = len([pic for pic in pic_list if len(pic) == 1]) # checks how many pictures have not yet been graded
    print('\nYou have %d pictures left to grade in this set.' % pics_to_grade)
    print('Exiting grader, progress saved.')

if __name__ == '__main__':     #so you can import the above functions without running all this

#----------------------------------------------------------------------#
# Variable declarations

    pic_list = []
    params = sys.argv

#----------------------------------------------------------------------#
# Main function

    folder_name = find_folder_name()
    if not folder_name:
        print('Make sure the folder of pictures to grade is in this directory')
        raise Exception

    grades_file = folder_name + "_grades.csv" #automatic name for the grades csv

    # checks to see if csv needs setup
    if len(params) > 1 and params[1] == 'n':
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

        print("\nWelcome to the Garbage Grader! Drag the picture-viewing window"
              " to a convenient place, then press enter to begin grading.")
        shutil.copy('placeholder.jpg', 'current_pic.jpg')
        os.system('start current_pic.jpg')  # opens current_pic.jpg in the default photo viewer
        input()                             # waits for the user to press enter

        print("You have %d pictures left to grade in this set... Let's begin!\n"
              "At any time, you may enter 'q' to quit or '#' to see how many"
              " pictures are left.\n" % pics_to_grade)
        time.sleep(1)

        # This sets up the random sample with no repeats of the picture that we want to pull from all numbers will have 1 added as the 0th picture doesn't matter in this case, and the last picture does.
        sample = random.sample(range(len(pic_list)),len(pic_list))

        # Iterating through each of the pictures in the list. Copies the pictures into current_pic.jpg and then takes in the grade of commandline. Can break out with Ctrl c.
        for i in sample:
            id = int(pic_list[i][0])
            if len(pic_list[i]) == 1: #if it still needs a grade
                try:
                    id_str = format(id, '06d')

                    file_path = folder_name + '\\' + id_str + '.jpg'
                    shutil.copy(file_path, 'current_pic.jpg') #copy the picture into current_pic.jpg, which is already pulled up in the default photo viewer

                    grade = input("What grade would you give this picture (%s.jpg)?\n" % id_str).strip().upper()

                    while grade == '#':
                        pics_to_grade = len([pic for pic in pic_list if len(pic) == 1]) # checks how many pictures have not yet been graded
                        print('\nYou have %d pictures left to grade in this set.' % pics_to_grade)
                        grade = input("\nWhat grade would you give this picture (%s.jpg)?\n" % id_str).strip().upper()

                    if grade == 'Q':
                        raise KeyboardInterrupt


                    pic_list[i].append(grade)
                except Exception as e:
                    print(e)
                    print("Make sure you aren't grading too quickly...") # the try sometimes throws an error if I grade really fast
                    early_quit(grades_file, pic_list)
                    break
                except KeyboardInterrupt:
                    early_quit(grades_file, pic_list)
                    break
        else:
            # writes to the csv file
            write_csv(grades_file, pic_list)
            print('\nDone grading! All grades have been saved in the "%s" file.' % grades_file)
    else:
        print('There are no pictures left to grade in this set.')
