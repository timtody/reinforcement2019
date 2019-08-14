import library.logger as lg
from matplotlib import pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
import sys
import argparse
import os

color_schemes = {
    "green": {"light": "#99c4a0", "dark": "#276631"},
    "orange": {"light": "#facfa5", "dark": "#ff560e"},
    "blue" : {"light": "#88aab5", "dark": "#1c4957"},
}
handles = ["a)", "b)", "c)", "d)", "e)", "f)"]

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

def plot(log, ax, name, color, handle, showylabel):
    x = list(range(1,len(log.pacmanReward[:global_cutoff])+1))
    y = log.pacmanReward[:global_cutoff]

    # "get" (cheat) optimum
    y_max = np.max(y)
    opt = np.ones(len(x)) * y_max

    y_smooth = rolling_average(y, 333)
    ax.scatter(x[::skip], y[::skip], c=color_schemes[color]["light"],s=scatter_size)
    ax.plot(x[::skip], y_smooth[::skip], c=color_schemes[color]["dark"], label=handle)
    ax.plot(opt, linestyle="--", color="gray")
    legend = ax.legend(loc='upper left', handlelength=0)
    if showylabel: ax.set(ylabel="Total reward per game")


# cli parsing
parser = argparse.ArgumentParser()
parser.add_argument('path')
parser.add_argument('--color', default="orange")
args = parser.parse_args()
color = args.color
path = args.path

files = [os.path.abspath(path + '\\' + f) for f in os.listdir(path)]
file_names_only = os.listdir(path)
logs = []
# we list all files in the spcified path - please put only .pickle files there
for f in files:
    logs.append(lg.Logger(loadPath=f))

# we create a horizonzal plot for each file
nrows = len(logs)

import matplotlib
from matplotlib.backends.backend_pgf import FigureCanvasPgf
matplotlib.backend_bases.register_backend('pdf', FigureCanvasPgf)
sns.set(context="paper")

# shared x and y labels
fig, axes = plt.subplots(nrows=nrows, ncols=1, sharex=True, sharey=True)

plt.xlabel('Number of games played')
plt.tight_layout()
scatter_size = 0.8
skip = 40 # adjust depending on granularity and available memory - this easily overflows when generating a pgf
global_cutoff = 50000


axes = [axes] if nrows == 1 else axes # oof (thanks python)

# now do the actual plotting
for i, log in enumerate(logs):
    showylabel = True if i == len(logs) // 2 else False
    plot(log, axes[i], file_names_only[i], color, handles[i], showylabel)

plt.savefig("test.pdf")
plt.savefig("test.pgf")
