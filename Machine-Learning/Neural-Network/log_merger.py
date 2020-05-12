import os, csv

grade_log = 'grade_log.csv'
scale_log = 'scale_log.csv'

def write_csv(fp,data):
    with open(fp, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerows(data)


with open('scale_log.csv') as scale_log:
    scale_list = list(csv.reader(scale_log, delimiter=','))

with open('grade_log.csv') as grade_log:
    grade_list = list(csv.reader(grade_log, delimiter = ','))

scale_dict = {entry[1]: (entry[0], round(float(entry[3]))) for entry in scale_list
  if entry[2] == 'food added'}
#print(scale_dict)

merged_list = [['Time', 'ID', 'Weight', 'Grade', 'A_prob', 'B_prob', 'C_prob', 'D_prob',
    'F_prob', 'N_prob']]

for time, ID, grade, A, B, C, D, F, N in grade_list[1:]:
    #print(time, ID, grade, A, B, C, D, F, N)
    merged_list.append([scale_dict[ID][0], ID, scale_dict[ID][1], grade,
    A, B, C, D, F, N])

write_csv('merged_log.csv', merged_list)
