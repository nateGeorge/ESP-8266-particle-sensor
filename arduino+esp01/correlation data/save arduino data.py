import serial, requests, re, csv, os
from datetime import datetime

ser = serial.Serial(1,timeout=3)

datafile = datetime.now().isoformat() + ' arduino data.csv'
P1ratio = None
if not os.path.isfile(datafile):
    with open(datafile,'wb') as csvfile:
        arduinocsv = csv.writer(csvfile, delimiter = ',')
        arduinocsv.writerow(['P2 ratio', 'P1 ratio', '0.5um', '1um', 'time (iso)'])

while True:
    line = ser.readline()
    if line!='':
        if re.search('.*P1: (\d+\.\d+).*', line):
            P1conc = re.search('.*P1: (\d+\.\d+).*', line).group(1)
        if re.search('.*P1 ratio: (\d+\.\d+).*', line):
            P1ratio = re.search('.*P1 ratio: (\d+\.\d+).*', line).group(1)
        if re.search('.*P2: (\d+\.\d+).*', line):
            P2conc = re.search('.*P2: (\d+\.\d+).*', line).group(1)
        measureTime = datetime.now().isoformat()
        if re.search('.*P2 ratio: (\d+\.\d+).*', line) and P1ratio != None:
            P2ratio = re.search('.*P2 ratio: (\d+\.\d+).*', line).group(1)
            print 'P1, P2 ratios:', P1ratio, P2ratio
            print 'P1, P2 concs:', P1conc, P2conc
            with open(datafile,'ab+') as csvfile:
                arduinocsv = csv.writer(csvfile, delimiter = ',')
                arduinocsv.writerow([P2ratio, P1ratio, P2conc, P1conc, measureTime])