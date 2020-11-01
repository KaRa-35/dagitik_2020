import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

sensor_macs = ["001583e5a5bd", "001583e5b269", "001583e5a3c0", "001a7dda710b"]
transmitter_macs = ["e78f135624ce", "f963ea9bb3ea"]

data = pd.read_csv("D:\lab.txt")

#bu fonsiyon a trnsmitter b de sensör olacak şekilde verilen ikilinin rssi bar plot'ını gösterir

def bar(a,b):
    histogram = np.array(data.loc[data["transmitter_mac"] == transmitter_macs[a]].loc[data["sensor_mac"] == sensor_macs[b]].rssi)
    histogram_counts = []
    for i in range(max(histogram) - min(histogram) + 1):
        histogram_counts.append(np.count_nonzero(histogram == min(histogram) + i))
    plt.bar(range(min(histogram), max(histogram) + 1), histogram_counts)
    plt.title(transmitter_macs[a]+" ,  "+sensor_macs[b])
    plt.show()
for i in range(2):
    for j in range(4):
        bar(i,j)