import serial, requests, re, csv, os
from datetime import datetime

ser = serial.Serial(8,timeout=3)

datafile = 'correlation data/' + datetime.strftime(datetime.now(),'%Y-%m-%d %H-%M-%S') + ' dylos data.csv'
if not os.path.isfile(datafile):
    with open(datafile,'wb') as csvfile:
        dyloscsv = csv.writer(csvfile, delimiter = ',')
        dyloscsv.writerow(['1um', '5um', 'time (iso)'])

while True:
    line = ser.readline()
    if line!='':
        match = re.search('(\d+),(\d+)',line)
        smallCount = match.group(1)
        largeCount = match.group(2)
        print '1um: ', smallCount, '5um: ', largeCount
        measureTime = datetime.now().isoformat()
        with open(datafile,'ab+') as csvfile:
            dyloscsv = csv.writer(csvfile, delimiter = ',')
            dyloscsv.writerow([smallCount, largeCount, measureTime])