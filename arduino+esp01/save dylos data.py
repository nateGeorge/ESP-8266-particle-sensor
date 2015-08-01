import serial, requests, re, csv, os
from datetime import datetime

ser = serial.Serial(4,timeout=10)

datafile = 'dylos data.csv'

if not os.path.isfile(datafile):
    with open(datafile,'a+') as csvfile:
        dyloscsv = csv.writer(csvfile, delimiter = ',')
        dyloscsv.writeline('1um', '5um', 'time (iso)')

with open(datafile,'a+') as csvfile:
    while True:
        line = ser.readline()
        if line!='':
            match = re.search('(\d+),(\d+)',line)
            smallCount = match.group(1)
            largeCount = match.group(2)
            print '1um: ', smallCount, '5um: ', largeCount
            measureTime = datetime.now().isoformat()
            dyloscsv = csv.writer(csvfile, delimiter = ',')
            dyloscsv.writeline(smallCount, largeCount, measureTime)