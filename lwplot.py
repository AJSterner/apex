"""
provides various functions for plotting longwave data
"""
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt

def xyreduce(x, y, sample='lin', factor=16384):
    """
    reduces array by a factor of ~groupsize/3 by taking the min, max and mean of each
    group. The groupsizes can be constant or logaritmic based on 'sample'
    returns reduced ndarrays
    """
    assert x.size == y.size, 'arrays must have same length, {}, {}'.format(
        x.size, y.size)
    per_sample = 3
    samples = y.size // factor
    assert samples > 0, 'factor must be less than array size. factor: {}, array: {}'.format(
        factor, y.size)
    new_size = samples * per_sample

    assert sample == 'lin' or sample == 'log', 'sample must be either \'lin\' or \'log\''

    if sample == 'lin':
        idx = np.arange(0, y.size + factor, factor)
    else:
        idx = np.logspace(0, np.log10(y.size), samples + 1).astype(np.int_)

    new_x = np.empty(new_size, dtype=x.dtype)
    new_y = np.empty(new_size, dtype=y.dtype)

    assert isinstance(samples, int), "samples is {}, a {}".format(samples, type(samples))
    for i in range(samples):
        low = idx[i]
        high = idx[i + 1]
        if high == low:
            high += 1

        x_slice = x[low:high]
        y_slice = y[low:high]

        new_x[i * per_sample: (i + 1) * per_sample] = [x_slice[y_slice.argmin()],
                                                       x_slice.mean(), x_slice[y_slice.argmax()]]
        new_y[i * per_sample: (i + 1) * per_sample] = [y_slice.min(),
                                                       y_slice.mean(), y_slice.max()]

    return new_x, new_y


def plot(ax, x, y, reduced, *args):
    """ plots x and y on axis x with args"""
    if reduced:
        x, y = xyreduce(x, y)
    ax.plot(x, y, *args)


def loglog(ax, x, y, reduced, *args):
    """ plots x and y on axis x with args"""
    if reduced:
        x, y = xyreduce(x, y, 'log')
    ax.loglog(x, y, *args)


def semilogx(ax, x, y, reduced, *args):
    """ plots x and y on axis x with args"""
    if reduced:
        x, y = xyreduce(x, y, 'log')
    ax.loglog(x, y, *args)
    # ax.tick_params(axis='y',
    #                reset=True,
    #                which='both',
    #                right='on',
    #                labelsize='large')


def plot_middle(ax1, x, y, dsize, reduce):
    """ plots data for middle graphs"""
    # y = y * np.hanning(dsize)
    # y = y[dsize-y.size:] * np.hanning(dsize)[dsize-y.size:]
    fft = abs(np.fft.fft(y))[:dsize/2]
    loglog(ax1, x[:dsize/2], fft, reduce)

    # ax1.tick_params('y', colors='b')
    # ax2 = ax1.twinx()
    # semilogx(ax2, x[:size], np.sqrt(np.cumsum((fft)**2)), reduce, 'r')
    # ax2.tick_params('y', colors='r')

def nplot_middle(ax1, x, y, reduce):
    fft = abs(np.fft.fft(y * np.hanning(y.size)))[:y.size/2]
    loglog(ax1, x[:y.size/2], fft, reduce)
    xlo, xhi = plt.xlim()
    plt.xlim([10**-1, xhi])

# TODO: use reduce on x and y (remember to turn of sample step)
def plot_bottom(ax, z, heatmap, *args):
    """ plots data for bottom graphs"""
    if heatmap:
        plot_heatmap(ax, z.real, z.imag)
    else:
        
        # x1, y1 = xyreduce(x, y, 'lin', 4096)
        # y2, x2 = xyreduce(y, x, 'lin', 4096)
        # ax.plot(np.append(x1, x2), np.append(y1, y2), *args)
        theta = np.angle(z.mean())
        z = z * np.exp(-1j * theta)
        x = z.real
        y = z.imag
        width = max(x.max() - x.min(), y.max() - y.min())
        ax_width = .6 * width
        ax.plot(x, y, *args)

        plt.xlim([x.mean() - ax_width, x.mean() + ax_width])
        plt.ylim([y.mean() - ax_width, y.mean() + ax_width]) #set plt ranges


def plot_heatmap(ax, x, y):
    """generates a heatmap from data"""
    heatmap, xedges, yedges = np.histogram2d(x, y, bins=100)
    extent = [xedges[0], xedges[-1], yedges[0], yedges[-1]]
    thresh = 1
    # fill the areas with low density by NaNs
    heatmap[heatmap < thresh] = np.nan

    ax.imshow(heatmap.T, cmap='jet', extent=extent, origin='lower')


def plot_phase(ax, x, z, reduce, *args):
    y = np.unwrap(np.angle(z) - np.angle(z.mean()))
    if reduce:
        x, y = xyreduce(x, y)
    ax.plot(x, y, *args)
