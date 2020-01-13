import csv, os, shutil, time

def find_folder_name():
    for item in os.scandir():
        if item.is_dir() and item.name.startswith("Set_"):
            return item.name
    else:
        return False

def place(pic_name, grade):
    shutil.copy(pic_folder + '\\' + pic_name, sorted_name + '\\' + grade + '\\' + pic_name)

def alert(path, message, id):
    os.system('start JPEGView64\\JPEGView ' + path)
    print("\nAlert: Grader %d gave this picture a grade of '%s', which is not recognized."
            % (id, message))
    input('Press enter to acknowledge: ')
    print()

def consult(path, all_grades):
    os.system('start JPEGView64\\JPEGView ' + path)
    print('\nThese were the grades given to this picture:')
    for grader, grade in enumerate(all_grades):
        print('Grader %d: %s' % (grader + 1, grade))
    grade = 'ERROR'
    while grade not in list('ABCDFN'):
        grade = input('What grade would you like to assign it? ').upper().strip()
    print()
    return grade

print('Sorting...\n')

pic_folder = find_folder_name()
set_name = pic_folder[:-4]
sorted_name = set_name + '_sorted'

num_graders = 3
grades = []

grader = 0

try:
    os.mkdir(sorted_name)
except FileExistsError:
    pass

for letter in 'ABCDFN':
    sub_dir = sorted_name + '\\' + letter
    try:
        os.mkdir(sub_dir)
    except FileExistsError:
        pass
    for file in os.scandir(sub_dir):
        os.remove(file)

for file in os.scandir('grades'):
    csv_file = open(file)
    csv_reader = csv.reader(csv_file, delimiter=',')
    these_grades = {}
    for pic_num, grade in csv_reader:
        these_grades[int(pic_num)] = grade
    csv_file.close()
    grades.append(these_grades)
    grader += 1

categories = {'unanimous': 0, 'two-to-one': 0, 'median of three': 0, 'had to consult': 0}

for pic in os.scandir(pic_folder):
    num = int(pic.name[:-4])
    print(num)
    #print(num)
    all_grades = [grades[i][num] for i in range(num_graders)]
    #print(all_grades)
    for grader, grade in enumerate(all_grades):
        if grade not in list('ABCDFN'):
            alert(pic.path, grade, grader + 1)
    num_unique = len(set(all_grades))
    if num_unique == 1:
        grade = all_grades[0]
        if grade in list('ABCDFN'):
            categories['unanimous'] += 1
        else:
            categories['had to consult'] += 1
            grade = consult(pic.path, all_grades)
    elif num_unique == 2:
        if all_grades.count(all_grades[0]) == 2:
            grade = all_grades[0]
        else:
            grade = all_grades[1]
        if grade in list('ABCDFN'):
            categories['two-to-one'] += 1
        else:
            categories['had to consult'] += 1
            grade = consult(pic.path, all_grades)
    else:
        if set(all_grades).difference(set('ABCDF')):
            categories['had to consult'] += 1
            grade = consult(pic.path, all_grades)
        else:
            categories['median of three'] += 1
            grade = sorted(all_grades)[1]
    #print(grade)
    place(pic.name, grade)

print('\nDone sorting!\n\nCategory totals:')

for category, number in categories.items():
    print(category + ': ' + str(number))
print('total:', sum(categories.values()), end = '\n\n')

time.sleep(3)
os.system('taskkill /IM JPEGView.exe /f')
