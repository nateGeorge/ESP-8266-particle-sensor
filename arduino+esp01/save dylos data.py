import serial, requests, re, csv, os
from datetime import datetime

ser = serial.Serial(8,timeout=10)

datafile = 'dylos data.csv'

if not os.path.isfile(datafile):
    with open(datafile,'a+') as csvfile:
        dyloscsv = csv.writer(csvfile, delimiter = ',')
        dyloscsv.writerow(['1um', '5um', 'time (iso)'])

with open(datafile,'a+') as csvfile:
    dyloscsv = csv.writer(csvfile, delimiter = ',')
    while True:
        line = ser.readline()
        if line!='':
            match = re.search('(\d+),(\d+)',line)
            smallCount = match.group(1)
            largeCount = match.group(2)
            print '1um: ', smallCount, '5um: ', largeCount
            measureTime = datetime.now().isoformat()
            dyloscsv.writerow([smallCount, largeCount, measureTime])