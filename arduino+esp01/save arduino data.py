import serial, requests, re, csv, os
from datetime import datetime

ser = serial.Serial(1,timeout=10)

datafile = 'arduino data.csv'

if not os.path.isfile(datafile):
    with open(datafile,'a+') as csvfile:
        arduinocsv = csv.writer(csvfile, delimiter = ',')
        arduinocsv.writeline('0.5um', '1um', 'time (iso)')

with open(datafile,'a+') as csvfile:
    while True:
        line = ser.readline()
        if line!='':
            match = re.search('(\d+),(\d+)',line)
            smallCount = match.group(1)
            largeCount = match.group(2)
            print '1um: ', smallCount, '5um: ', largeCount
            measureTime = datetime.now().isoformat()
            arduinocsv = csv.writer(csvfile, delimiter = ',')
            arduinocsv.writeline(smallCount, largeCount, measureTime)