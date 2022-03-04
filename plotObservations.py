########################################################
# Convert the modulo timestamp back to epoch time      #
# To be used with generate-test-traffic.py             #
# See https://headintheclouds.site/episodes/episode18  #
########################################################

import sys
from numpy import genfromtxt
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl

def plotData(start, stop, filename):
    fig = plt.figure()
    axis1 = fig.add_subplot(311)
    axis1.plot(SrcPort[start:stop],IngestDelaySecs[start:stop])
    axis1.set_ylabel("Ingest\nDelay Secs")
    axis1.set_yticks(range(60,700, 120))
    axis1.grid()
    axis2 = fig.add_subplot(312, sharex=axis1)
    axis2.plot(SrcPort[start:stop],TimeStampErrorSecs[start:stop], 'r')
    axis2.set_ylabel("Timestamp\nError Secs")
    axis2.grid()
    axis3 = fig.add_subplot(313, sharex=axis1)
    axis3.scatter(SrcPort[start:stop],MissingData[start:stop])
    axis3.set_ylabel("Missing Data")
    axis3.set_yticks([])
    axis3.grid()
    plt.savefig(filename)



array = genfromtxt('logs-insights-results.csv', delimiter=',', names=True, usecols=(8,2,7), dtype=[int,float,int])

x = []
for i in range(0,len(array)):
    x.append(array[i][0])

SrcPort=[]
IngestDelaySecs=[]
IngestDelayMins=[]
TimeStampErrorSecs=[]
MissingData = []
MissingDataSrcPort = []
SecsBetweenMissingData = []
for i in range(min(x),max(x)):
    if i not in x:
        SrcPort.append(i)
        IngestDelaySecs.append(None)
        IngestDelayMins.append(None)
        TimeStampErrorSecs.append(None)
        MissingData.append(1)
        MissingDataSrcPort.append(i)
    else:
        j = x.index(i)
        SrcPort.append(array[j][0])
        IngestDelaySecs.append(array[j][1])
        IngestDelayMins.append(array[j][1] / 60)
        TimeStampErrorSecs.append(array[j][2])
        MissingData.append(None)


plotData(1000, 2000, "plot1.png")
plotData(1020, 1200, "plot2.png")
plotData(1, len(SrcPort), "plot3.png")

for k in range(1, len(MissingDataSrcPort)):
    delta = MissingDataSrcPort[k] - MissingDataSrcPort[k - 1]
    SecsBetweenMissingData.append(delta)

fig = plt.figure()
ax = fig.add_subplot(111)
plt.plot(SecsBetweenMissingData)
plt.title('Seconds Between Missing Data')
ax.grid()
ax.set_yticks(range(0,240,15))
ax.set_ylabel("Seconds")
ax.set_xlabel("Missing Data Item")
plt.savefig('delta.png')

print("The following srcPorts are missing:")
print(MissingDataSrcPort)

f2 = open("missingSrcPorts.csv", "w")

for port in MissingDataSrcPort:
    f2.write('"' + str(port) + '"\n')
f2.close()
