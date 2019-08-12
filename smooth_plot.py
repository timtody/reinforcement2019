import library.logger as lg
from matplotlib import pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
import sys
import argparse
import os

def rolling_average(data, window_size=999):
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


parser = argparse.ArgumentParser()
parser.add_argument('path')
parser.add_argument('--color', default="orange")
args = parser.parse_args()
path = args.path
color = args.color


fullPathToHistoryPickle = path
logs = lg.Logger(loadPath=fullPathToHistoryPickle)

# plotting
x = list(range(1,len(logs.pacmanReward)+1))
y = logs.pacmanReward
y_smooth = rolling_average(y, 333)

import matplotlib
from matplotlib.backends.backend_pgf import FigureCanvasPgf
matplotlib.backend_bases.register_backend('pdf', FigureCanvasPgf)

color_schemes = {
    "green": {"light": "#99c4a0", "dark": "#276631"},
    "orange": {"light": "#facfa5", "dark": "#ff560e"},
    "blue" : {"light": "#88aab5", "dark": "#1c4957"},
}

dir = r'C:\Users\Julius\Uni\sose19\rl\PacMan'
#plt.style.use(os.path.join(dir, 'report.mplstyle'))

sns.set(context="paper")

# shared x and y labels
fig, axes = plt.subplots(nrows=3, ncols=1, sharex=True, sharey=True)

plt.xlabel('Number of games played')
plt.tight_layout()
scatter_size = 0.8
skip = 32
axes[0].scatter(x[::skip], y[::skip], c=color_schemes["orange"]["light"],s=scatter_size)
axes[0].plot(x[::skip], y_smooth[::skip], c=color_schemes["orange"]["dark"], label="Model A")
#legend.get_frame().set_facecolor('C0')
legend = axes[0].legend(loc='upper left')


axes[1].scatter(x[::skip], y[::skip], c=color_schemes["green"]["light"], s=scatter_size)
axes[1].plot(x[::skip], y_smooth[::skip], c=color_schemes["green"]["dark"], label="Model B")
axes[1].set(ylabel="Reward")
legend = axes[1].legend(loc='upper left')


axes[2].scatter(x[::skip], y[::skip], c=color_schemes["blue"]["light"],s=scatter_size)
axes[2].plot(x[::skip], y_smooth[::skip], c=color_schemes["blue"]["dark"], label="Model C")
legend = axes[2].legend(loc='upper left')


plt.savefig("test.pdf")
plt.savefig("test.pgf")
