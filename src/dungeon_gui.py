import numpy as np
import pandas as pd
from collections import deque
from matplotlib import pyplot as plt
from skimage.io import imread, imsave, imshow
from skimage import filters
from skimage.morphology import disk
from matplotlib.patches import Rectangle
from matplotlib.widgets import RectangleSelector
from pylab import *
import pickle
import time
from dungeon_code import *

class DungeonScreen():

    def __init__(self, d):
        self.d = d
        self.fig, self.ax = plt.subplots()
        self.ax.axis('off')
        self.draw_background()
        plt.show()

    def draw_background(self):
        background = imread('../images/parchment.jpg')
        self.ax.imshow(background)

    def 

def main():
    d = DungeonHandler('jeeves','bubbletoot','devil mcflickster', 'falingard', 'vordorim')
    ds = DungeonScreen(d)

if __name__ == '__main__':
    main()
