import library.logger as lg
from matplotlib import pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np

def rolling_average(data, window_size):
    # window size can only be odd
    # we compute a padding dependant on the window size
    data = np.copy(data)
    padding_size = window_size//2
    data_out = np.empty(shape=(len(data) + padding_size*2))
    data_in = np.empty(shape=(len(data) + padding_size*2))
    data_in[padding_size:padding_size+len(data)] = data
    # compute padding
    # padding is computed as the mean of the first and last
    # *padding_size* elements in the array
    padding_left = np.mean(data[:padding_size])
    data_in[:padding_size] = padding_left
    padding_right = np.mean(data[len(data)-1:])
    data_in[len(data):] = padding_right

    # compute rolling average
    for i, elem in enumerate(data):
        data[i] = np.mean(data_in[i:i+window_size])
    return data

fullPathToHistoryPickle = "/mnt/c/Users/Julius/Uni/experiments/rl_pacman_2019-8-10_2/history.pickle"

logs = lg.Logger(loadPath=fullPathToHistoryPickle)


sns.set()
x = list(range(1,len(logs.pacmanReward)+1))
y = logs.pacmanReward
y_smooth = rolling_average(y, 999)



import matplotlib as mpl

#mpl.use("pgf")


plt.plot(x, y, c="#facfa5")
plt.plot(x, y_smooth, c="#ff560e")
plt.savefig("test.pgf")
plt.savefig("test.pdf")