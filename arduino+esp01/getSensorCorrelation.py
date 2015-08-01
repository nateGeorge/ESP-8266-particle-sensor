import pandas as pd
import numpy as np
from datetime import datetime
from dateutil.parser import parse
from scipy import interp
import pylab as plt
plt.style.use('dark_background')

arduinoDataFile = 'arduino data.csv'
dylosDataFile = 'dylos data.csv'

arduinoData = pd.read_csv(arduinoDataFile)
dylosData = pd.read_csv(dylosDataFile)

arduinoTime = [(parse(eachTime) - datetime(1970, 1, 1)).total_seconds() for eachTime in arduinoData['time (iso)']]
dylosTime = [(parse(eachTime) - datetime(1970, 1, 1)).total_seconds() for eachTime in dylosData['time (iso)']]

interpArduinoTime = interp(dylosTime, arduinoTime, arduinoTime)#arduinoData['1um'])
interpArduinoData = interp(dylosTime, arduinoTime, arduinoData['1um'])
interpArduinoRatio = interp(dylosTime, arduinoTime, arduinoData['P1 ratio'])

interpTimes = []
dylos1umData = []
arduino1umData = []
arduinoP1ratio = []
for each in range(len(interpArduinoTime)):
    if dylosTime[each] == interpArduinoTime[each]:
        interpTimes.append(dylosTime[each])
        dylos1umData.append(dylosData['1um'][each])
        arduino1umData.append(interpArduinoData[each]*2.5)
        arduinoP1ratio.append(interpArduinoRatio[each])
rollingP1ratio = pd.rolling_mean(np.array(arduinoP1ratio),10)
for each in range(len(rollingP1ratio)):
    if np.isnan(rollingP1ratio[each]):
        rollingP1ratio[each] = interpArduinoRatio[each]
P1fit = np.polyfit(rollingP1ratio, dylos1umData, deg=1)
P1corr = np.poly1d(P1fit)
minRatio = min(rollingP1ratio)
maxRatio = max(rollingP1ratio)
fitLineX = np.linspace(minRatio, maxRatio, 10)
fitLineY = P1corr(fitLineX)
print P1fit

allData = {}
allData['epoch time'] = interpTimes
allData['dylos data'] = dylos1umData
allData['arduino data'] = arduino1umData
allData = pd.DataFrame(allData)
allData = allData.set_index('epoch time')

corrData = {}
corrData['dylos 1um'] = dylos1umData
corrData['P1 ratio'] = rollingP1ratio

corrData = pd.DataFrame(corrData)
ax = corrData.plot(kind = 'scatter', x='P1 ratio', y='dylos 1um', c='white')
ax.plot(fitLineX, fitLineY)
plt.show()

allData.plot()
plt.show()

plt.scatter(allData.index, arduinoP1ratio, label='raw data')
plt.plot(allData.index, rollingP1ratio, label='mva', c='w')
plt.legend(loc='best')
plt.show()