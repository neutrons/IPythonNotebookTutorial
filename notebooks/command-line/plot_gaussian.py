#!/usr/bin/env python

import numpy as np
from matplotlib import pyplot as plt

def gaussian(x, center, sigma):
    return np.exp(-(x-center)**2/2/sigma/sigma)/sigma/np.sqrt(2*np.pi)

x = np.linspace(-10, 10, 100)
y = gaussian(x, 0, 3)
plt.plot(x,y)
plt.show()
