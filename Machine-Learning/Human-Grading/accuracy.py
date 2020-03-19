import csv

base_dir = 'C:/Users/Ben/Code/GarbageGraderData/TrainingData/'
set_num = input("Enter set number: ")

base_path = str.format('%sSet_%s/Set_%s_grades/Set_%s_grades_'
    % (base_dir, set_num, set_num, set_num))

grades = {}

total_displayed = {}
matches = {}
within_1 = {}


displayed_grades = 'ABCDF'

for grader in ['1', '2', '3', 'resolved']:
    csv_file = open(base_path + grader + '.csv')
    csv_reader = csv.reader(csv_file, delimiter=',')
    grades[grader] = list(csv_reader)
    total_displayed[grader] = 0
    matches[grader] = 0
    within_1[grader] = 0

for index, grade_pair in enumerate(grades['resolved']):
    official_grade = grade_pair[1]
    for grader in ['1', '2', '3', 'resolved']:
        if grade_pair[0] != grades[grader][index][0]:
            raise Exception # shouldn't ever happen; IDs don't match up
        grader_grade = grades[grader][index][1]
        if grader_grade in displayed_grades:
            total_displayed[grader] += 1
            if grader_grade == official_grade:
                matches[grader] += 1
            if (official_grade in displayed_grades
                and abs(displayed_grades.index(grader_grade)
                - displayed_grades.index(official_grade)) <= 1):
                within_1[grader] += 1

total = len(grades['resolved'])
print('total displayed:', total_displayed)
print('\nmatches:', matches)
print('match accuracies:', [round(matches / total_displayed[grader], 2)
                            for grader, matches in matches.items()])
print('\nwithin 1:', within_1)
print('within 1 accuracies:', [round(within_1 / total_displayed[grader], 2)
                            for grader, within_1 in within_1.items()])
