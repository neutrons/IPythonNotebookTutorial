#!/usr/bin/env python

import numpy as np
from matplotlib import pyplot as plt

def gaussian(x, center, sigma):
    return np.exp(-(x-center)**2/2/sigma/sigma)/sigma/np.sqrt(2*np.pi)

def plot(width):
    x = np.linspace(-10, 10, 100)
    y = gaussian(x, 0, width)  # use argument here
    plt.plot(x,y)
    return

import tqdm
import time
for w in tqdm.tqdm(np.logspace(-1, 1, 10)):
    time.sleep(1)
    plot(w)
    continue
plt.show()
