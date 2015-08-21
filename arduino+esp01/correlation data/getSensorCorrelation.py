import os, re, time
import pandas as pd
import numpy as np
import pylab as plt
from datetime import datetime
from dateutil.parser import parse
from scipy import interp
from scipy.optimize import curve_fit as cf
from datetime import timedelta

mvaperiod = 20

#timeCutoff = datetime(2015,8,1,14)
#timeCutoff = (timeCutoff - datetime(1970,1,1)).total_seconds()

def func(x, a, b, c):
    return np.power(x,3)*a + np.power(x,2)*b + x*c
    
def expfunc(x, a, b):
    return np.exp(a*x)*b
    
def linearfunc(x, a):
    return a*x

plt.style.use('dark_background')

# data from room in 93 ridgeview
#arduinoDataFile = '2015-08-06 21-14-21 arduino data.csv'
#dylosDataFile = '2015-08-06 21-15-04 dylos data.csv'

# factor e farm

firstArduinoFile = False
firstdylosFile = False
day = 17
corrFiles = os.listdir('correlation data')
arduinoFiles = []
dylosFiles = []
for file in corrFiles:
    if os.path.isfile():
        if re.search('2015-08-' + day, file):
            if re.search('arduino', file):
                arduinoFiles.append(file)
            if re.search('dylos', file):
                dylosFiles.append(file)

arduinoDataFile = 'correlation data/2015-08-18 10-16-48 arduino data.csv'
dylosDataFile = 'correlation data/2015-08-18 10-16-46 dylos data.csv'

arduinoData = pd.read_csv(arduinoDataFile)
dylosData = pd.read_csv(dylosDataFile)

arduinoTime = [(parse(eachTime) - datetime(1970, 1, 1)).total_seconds() for eachTime in arduinoData['time (iso)']]
dylosTime = [(parse(eachTime) - datetime(1970, 1, 1)).total_seconds() for eachTime in dylosData['time (iso)']]

interpArduinoTime = interp(dylosTime, arduinoTime, arduinoTime)#arduinoData['1um'])
interpArduinoData = interp(dylosTime, arduinoTime, arduinoData['1um'])
interpArduinoRatio = interp(dylosTime, arduinoTime, arduinoData['P1 ratio'])
rollingArduinoData = pd.rolling_mean(np.array(interpArduinoData), 20)
rollingArduinoRatio = pd.rolling_mean(np.array(interpArduinoRatio), 20)

frames = [dylosData, pd.DataFrame(data=interpArduinoData, columns=['1um arduino']), pd.DataFrame(data=interpArduinoRatio, columns=['arduino P1 ratio'])]
result = pd.concat(frames,axis=1)
result.to_csv(path_or_buf='concatd data.csv', index=False)

interpTimes = []
dylos1umData = []
arduino1umData = []
arduinoP1ratio = []
for each in range(len(interpArduinoTime) - mvaperiod):
    #print dylosTime[each], timeMax
    if dylosTime[each] == interpArduinoTime[each]:# and dylosTime[each] > timeMin and dylosTime[each] < timeMax:
        interpTimes.append(datetime.fromtimestamp(dylosTime[each]) - timedelta(hours=-4)) # -6 for west coast time, -4 for central
        datetime.fromtimestamp(dylosTime[each]) - timedelta(hours=-4)
        print datetime.fromtimestamp(dylosTime[each]) - timedelta(hours=-4)
        dylos1umData.append(dylosData['1um'][each])
        arduino1umData.append(interpArduinoData[each]*2.5)
        arduinoP1ratio.append(interpArduinoRatio[each])
rollingP1ratio = pd.rolling_mean(np.array(arduinoP1ratio), 20)
for each in range(len(rollingP1ratio)):
    if np.isnan(rollingP1ratio[each]):
        rollingP1ratio[each] = arduinoP1ratio[each]
P1fit = np.polyfit(rollingP1ratio, dylos1umData, deg=4)
P1corr = np.poly1d(P1fit)
minRatio = min(rollingP1ratio)
maxRatio = max(rollingP1ratio)
fitLineX = np.linspace(minRatio, maxRatio, 1000)
fitLineY = P1corr(fitLineX)
print '4th order:', P1fit

popt, pcov = cf(func, rollingP1ratio, dylos1umData)
print '3rd order 0-intercept:', popt
fitLineY2 = func(fitLineX, popt[0], popt[1], popt[2])

popt3, pcov3 = cf(expfunc, rollingP1ratio, dylos1umData)
print 'exponential:',popt3
fitLineY3 = expfunc(fitLineX, popt3[0], popt3[1])

linearpopt, linearpcov = cf(linearfunc, rollingP1ratio, dylos1umData)
print 'linear:',linearpopt
fitLineYlinear = linearfunc(fitLineX, linearpopt[0])

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
ax.plot(fitLineX, fitLineY, linewidth=3, label='4th degree')
ax.plot(fitLineX, fitLineY2, linewidth=3, label='3rd order, intercept=0')
ax.plot(fitLineX, fitLineY3, linewidth=3, label='exponential')
ax.plot(fitLineX, fitLineYlinear, linewidth=3, label='linear')
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