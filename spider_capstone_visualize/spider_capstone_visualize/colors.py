#!/usr/bin/env python3

import numpy as np
import matplotlib.pyplot as plt

# Import colormap
def get_colormap(num_points: int, colormap: str = 'viridis'):
    # Get the colormap backwards (dark to light)
    cmap = plt.get_cmap(colormap)
    gradient = np.linspace(0, 1, num_points)

    # Extract individual colors as RGBA list
    colors = cmap(gradient) #cmap.resampled()

    return colors, cmap

if __name__ == '__main__':
    colormap = get_colormap(10)