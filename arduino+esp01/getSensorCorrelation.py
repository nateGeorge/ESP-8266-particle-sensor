import pandas as pd
import numpy as np
from datetime import datetime
from dateutil.parser import parse
from scipy import interp
import pylab as plt

arduinoDataFile = 'arduino data.csv'
dylosDataFile = 'dylos data.csv'

arduinoData = pd.read_csv(arduinoDataFile)
dylosData = pd.read_csv(dylosDataFile)

print arduinoData.columns
print dylosData.columns

arduinoTime = [(parse(eachTime) - datetime(1970, 1, 1)).total_seconds() for eachTime in arduinoData['time (iso)']]
dylosTime = [(parse(eachTime) - datetime(1970, 1, 1)).total_seconds() for eachTime in dylosData['time (iso)']]

interpArduinoTime = interp(dylosTime, arduinoTime, arduinoTime)#arduinoData['1um'])
interpArduinoData = interp(dylosTime, arduinoTime, arduinoData['1um'])

interpTimes = []
dylos1umData = []
arduino1umData = []
for each in range(len(interpArduinoTime)):
    if dylosTime[each] == interpArduinoTime[each]:
        interpTimes.append(dylosTime[each])
        dylos1umData.append(dylosData['1um'][each])
        arduino1umData.append(interpArduinoData[each])
print dylos1umData
print arduino1umData

allData = {}
allData['epoch time'] = interpTimes
allData['dylos data'] = dylos1umData
allData['arduino data'] = arduino1umData
allData = pd.DataFrame(allData)
allData = allData.set_index('epoch time')
allData.plot()
plt.show()