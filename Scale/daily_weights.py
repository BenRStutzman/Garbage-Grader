import csv, os
from datetime import datetime, timedelta

def to_datetime_object(timestamp):
    date, time = timestamp.split()
    year, month, day = [int(num) for num in date.split('-')]
    hour, minute, second = [int(num) for num in time.split(':')]
    return datetime(year, month, day, hour, minute, second)

def just_date(time_date):
    return datetime(time_date.year, time_date.month, time_date.day)

def write_csv(fp,data):
    with open(fp, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerows(data)

start_date = datetime(2019, 11, 23)
end_date = datetime(2020, 1, 17)
daily_weights = {}
while start_date <= end_date:
    daily_weights[start_date] = {'log': [], 'weight': 0.0, 'removals': 0,
                                    'weighted removals': 0}
    start_date += timedelta(days = 1)

#print(daily_weights)

leftovers = {}

for file in os.scandir('Logs'):
    csv_file = open(file)
    csv_reader = csv.reader(csv_file, delimiter=',')
    for line in list(csv_reader)[1:]:
        timestamp, ID, action, bin_weight, item_weight = line[:5]
        time_date = to_datetime_object(timestamp)
        ID = int(ID) if ID else -1
        date = just_date(time_date)
        bin_weight = float(bin_weight) if bin_weight else 0.0
        item_weight = float(item_weight) if item_weight else 0.0
        entry = {'time': time_date, 'ID': ID, 'action': action,
                 'bin_weight': bin_weight, 'item_weight': item_weight}
        daily_weights[date]['log'].append(entry)

#print('\n\n\n\n\n\n\n\n\n')
#print(daily_weights[datetime(2019,12,2)])

print('\nLeftovers (?):')
for day, value in daily_weights.items():
    log = value['log']
    for entry in log:
        if entry['action'] == 'food added':
            break
    else:
        value['weight'] = 0.0;
        continue
    for index, entry in enumerate(log[::-1]):
        if entry['action'] in ['food added', 'scale reset']:
            final_weight = log[::-1][index - 1]['bin_weight']
            #print(day, final_weight)
            break
    if  final_weight > 1:
        print('%.1f kg left over on %d/%d!' % (final_weight, day.month, day.day))
        value['weight'] += final_weight
        daily_weights[day + timedelta(days = 1)]['weight'] -= final_weight
    for entry in log:
        if entry['action'] == 'bin removed':
            value['removals'] += 1
            if entry['bin_weight'] > 0:
                value['weighted removals'] += 1
                value['weight'] += entry['bin_weight']

print('\nDate\t\tWeight (kg)\tRemovals')
print('-'*65)

data =[['Date', 'Weight (kg)', 'Removals',]]

for day, value in daily_weights.items():
    data.append([str.format('%d-%d-%d' % (day.year, day.month, day.day)),
            value['weight'], value['removals']])

    print('%d-%02d-%02d\t%s\t\t%d' % (day.year, day.month, day.day, value['weight'], value['removals'],))

write_csv('daily_weights.csv', data)
