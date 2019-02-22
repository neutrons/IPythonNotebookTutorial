#!/usr/bin/env python

import numpy as np
from matplotlib import pyplot as plt

def gaussian(x, center, sigma):
    return np.exp(-(x-center)**2/2/sigma/sigma)/sigma/np.sqrt(2*np.pi)

import click

@click.command()
@click.option('--width', default=3., help='width')
def plot(width):
    x = np.linspace(-10, 10, 100)
    y = gaussian(x, 0, width)  # use argument here
    plt.plot(x,y)
    plt.show()
    return

plot()
