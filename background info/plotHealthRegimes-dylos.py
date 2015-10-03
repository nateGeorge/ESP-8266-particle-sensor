import numpy as np
import pylab as plt

plt.style.use('dark_background')

# dictionary with format -- regime : [(lower limit, higher limit in ug/m3), (lower limit, higher limit in AQI units), color for coloring the plot]
epaRegimes = {
'v. hazardous':                   [(350.5,500),(400,500), 'maroon'],
'hazardous':                        [(250.5,350.5),(300,400), 'maroon'],
'v. unhealthy':                   [(150.5,250.5),(200,300), 'purple'],
'unhealthy':                        [(55.5,150.5),(150,200), 'red'],
'part. unhealthy':   [(35.5,55.5),(100,150), 'orange'],
'moderate':                         [(12,35.5),(50,100), 'yellow'],
'good':                             [(0,12),(0,50),'green']
}

# dictionary with format -- regime [lower limit, higher limit in 1 um particles 
dylos1um = {
'very poor':                        [1000, 1160, 'maroon'],
'poor':                             [350, 1000, 'purple'],
'fair':                             [100, 350, 'red'],
'good':                             [50, 100, 'orange'],
'very good':                        [25, 50, 'yellow'],
'excellent':                        [0, 25, 'green']
}


def cancerEqn(x):
    # input micrograms/m3 PM2.5
    return 3.6 * x # 36% percent increase for every 10 ug increase of PM25
    
def microGramEqn(x):
    return 4. * np.power(10., -16) * np.power(x, 4) - 2. * np.power(10., -11) * np.power(x, 3) + 3. * np.power(10., -7) * np.power(x, 2) + 0.0014 * x

xRange = np.linspace(0, 50000, 10000)
micrograms = microGramEqn(xRange)
xRange2 = np.linspace(0, 2, 10000)
particles = np.interp(xRange2, micrograms, xRange) # converts micrograms to particles
f, (ax1, ax2) = plt.subplots(2, figsize=(8, 8))
ax1.plot(xRange2, particles)
xTicks = []
for regime in dylos1um:
    print regime
    print dylos1um[regime][1]
    print microGramEqn(dylos1um[regime][1])
    ax1.axvspan(microGramEqn(dylos1um[regime][0]), microGramEqn(dylos1um[regime][1]), alpha=0.5, color =dylos1um[regime][2])
    ax2.axvspan(microGramEqn(dylos1um[regime][0]), microGramEqn(dylos1um[regime][1]), alpha=0.5, color =dylos1um[regime][2])
    xTicks.append(microGramEqn((dylos1um[regime][0] + dylos1um[regime][1])/2))
plt.sca(ax1)
plt.xticks(xTicks, [regime for regime in dylos1um], rotation=90)
ax1.get_xaxis().set_tick_params(pad = -150)
ax2.plot(xRange2, cancerEqn(xRange2))
ax2.set_ylabel('% increase of lung cancer odds')
ax2.set_xlabel('$\mu$g/m$^3$ PM2.5')
ax1.set_ylabel('# particles >= 1$\mu$m')
plt.tight_layout()
ax1.set_xlim([min(xRange2),max(xRange2)])
ax2.set_xlim([min(xRange2),max(xRange2)])
plt.savefig('test.png',facecolor=f.get_facecolor())
mng = plt.get_current_fig_manager()
mng.window.state('zoomed')
plt.show()