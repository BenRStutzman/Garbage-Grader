import csv, os, shutil, time

def find_folder_name():
    for item in os.scandir():
        if item.is_dir() and item.name.startswith("Set_"):
            return item.name
    else:
        return False

def place(pic_name, pic_num, grade):
    shutil.copy(pic_folder + '\\' + pic_name, sorted_name + '\\' + grade + '\\' + pic_name)
    pic_list.append([pic_num, grade])
    distribution[grade] += 1

# code that writes a 2-d dictionary to a csv file
def write_csv(csv_name, data):
    with open(csv_name, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerows(data)

def alert(path, message, id):
    os.system('start JPEGView64\\JPEGView ' + path)
    print("\nAlert: Grader %d gave this picture an unrecognized grade of:\n%s\n"
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

pic_list = []
distribution = {'A': 0, 'B': 0, 'C': 0, 'D': 0, 'F': 0, 'N': 0}
pic_folder = find_folder_name()
set_name = pic_folder[:-4]
sorted_name = set_name + '_sorted'
try:
    os.remove('grades\\' + set_name + '_all_grades_resolved.csv')
except FileNotFoundError:
    pass

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

consistencies = {1 : 0, 2 : 0, 3 : 0}

for file in os.scandir('grades'):
    csv_file = open(file)
    csv_reader = csv.reader(csv_file, delimiter=',')
    these_grades = {}
    csv_list = list(csv_reader)
    for pic_num, grade in csv_list[:-30]:
        these_grades[int(pic_num)] = grade
    for pic_num, grade in csv_list[-30:]:
        if grade == these_grades[int(pic_num) - 1000000]:
            consistencies[grader + 1] += 1
    csv_file.close()
    grades.append(these_grades)
    grader += 1

categories = {'unanimous': 0, 'two-to-one': 0, 'median of three': 0, 'had to consult': 0}

for pic in os.scandir(pic_folder):
    num = int(pic.name[:-4])
    print(num)
    #print(num)
    all_grades = [grades[i][num] for i in range(num_graders)]
    sorted_grades = sorted(all_grades)
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
        if set(all_grades).difference(set('ABCDF')):
            categories['had to consult'] += 1
            grade = consult(pic.path, all_grades)
        else:
            categories['two-to-one'] += 1
            grade = sorted_grades[1]
    else:
        if ''.join(sorted_grades) in 'ABCDF':
            categories['median of three'] += 1
            grade = sorted_grades[1]
        else:
            categories['had to consult'] += 1
            grade = consult(pic.path, all_grades)
    #print(grade)
    place(pic.name, num, grade)

print('\nDone sorting!\n')

print('Distribution:\n')
pic_list[1].extend(['', 'Distribution'])
pic_list[2].extend(['','', ])
for grade, number in distribution.items():
    pic_list[1].append(grade)
    pic_list[2].append(number)
    print(grade + ':' + str(number))
total = sum(distribution.values())
print('total:', total, end = '\n\n')

print('Resolutions:\n')
pic_list[4].extend(['', 'Resolutions'])
pic_list[5].extend(['','', ])
for category, number in categories.items():
    pic_list[4].append(category)
    pic_list[5].append(number)
    print(category + ': ' + str(number))
total = sum(categories.values())
print('total:', total, end = '\n\n')

print('Consistency Ratings:\n')
pic_list[7].extend(['', 'Consistency Ratings:'])
pic_list[8].extend(['','', ])
for grader, rating in consistencies.items():
    pic_list[7].append(grader)
    pic_list[8].append(rating)
    print('Grader ' + str(grader) + ': ' + str(rating))

write_csv('grades\\' + set_name + '_all_grades_resolved.csv', pic_list)

time.sleep(3)
os.system('taskkill /IM JPEGView.exe /f')
