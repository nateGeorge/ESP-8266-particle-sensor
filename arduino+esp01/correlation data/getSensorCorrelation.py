import pandas as pd
import numpy as np
import pylab as plt
from datetime import datetime
from dateutil.parser import parse
from scipy import interp
from scipy.optimize import curve_fit as cf
from dateutil import tz
from datetime import timedelta

to_zone = tz.tzlocal()
from_zone = tz.tzutc()

mvaperiod = 20

#timeCutoff = datetime(2015,8,1,14)
#timeCutoff = (timeCutoff - datetime(1970,1,1)).total_seconds()

def func(x, a, b, c):
    return np.power(x,3)*a + np.power(x,2)*b + x*c
    
def expfunc(x, a, b):
    return np.exp(a*x)*b

plt.style.use('dark_background')

arduinoDataFile = '2015-08-02 09-18-19 arduino data.csv'
dylosDataFile = '2015-08-02 09-17-57 dylos data.csv'

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
for each in range(len(interpArduinoTime) - mvaperiod):
    if dylosTime[each] == interpArduinoTime[each]:
        interpTimes.append(datetime.fromtimestamp(dylosTime[each]) - timedelta(hours=5))
        dylos1umData.append(dylosData['1um'][each])
        arduino1umData.append(interpArduinoData[each]*2.5)
        arduinoP1ratio.append(interpArduinoRatio[each + mvaperiod/2])
rollingP1ratio = pd.rolling_mean(np.array(arduinoP1ratio),20)
for each in range(len(rollingP1ratio)):
    if np.isnan(rollingP1ratio[each]):
        rollingP1ratio[each] = interpArduinoRatio[each]
P1fit = np.polyfit(rollingP1ratio, dylos1umData, deg=4)
P1corr = np.poly1d(P1fit)
minRatio = min(rollingP1ratio)
maxRatio = max(rollingP1ratio)
fitLineX = np.linspace(minRatio, maxRatio, 1000)
fitLineY = P1corr(fitLineX)
print P1fit

popt, pcov = cf(func, rollingP1ratio, dylos1umData)
print popt
fitLineY2 = func(fitLineX, popt[0], popt[1], popt[2])

popt3, pcov3 = cf(expfunc, rollingP1ratio, dylos1umData)
print popt3
fitLineY3 = expfunc(fitLineX, popt3[0], popt3[1])

allData = {}
allData['time'] = interpTimes
allData['dylos data'] = dylos1umData
allData['arduino data'] = arduino1umData
allData = pd.DataFrame(allData)
allData = allData.set_index('time')

corrData = {}
corrData['dylos 1um'] = dylos1umData
corrData['P1 ratio'] = rollingP1ratio

corrData = pd.DataFrame(corrData)
ax = corrData.plot(kind = 'scatter', x='P1 ratio', y='dylos 1um', c='white')
ax.plot(fitLineX, fitLineY, linewidth=3, label='linear')
ax.plot(fitLineX, fitLineY2, linewidth=3, label='3rd order, intercept=0')
ax.plot(fitLineX, fitLineY3, linewidth=3, label='exponential')
ax.legend(loc='best')
plt.show()

ax = allData.plot()
ax.plot(allData.index,pd.rolling_mean(allData['arduino data'],20), label='mva', color='orange', linewidth=3)
plt.show()

plt.scatter(allData.index, arduinoP1ratio, label='raw data')
plt.plot(allData.index, rollingP1ratio, label='mva', c='orange', linewidth=3)
plt.xlim(min(allData.index),max(allData.index))
plt.legend(loc='best')
plt.show()