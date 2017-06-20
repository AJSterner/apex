"""
provides various functions for plotting longwave data
"""
import numpy as np
# from matplotlib import pyplot as plt

def xyreduce(x, y, sample='lin', factor=16384):
    """
    reduces array by a factor of ~groupsize/3 by taking the min, max and mean of each
    group. The groupsizes can be constant or logaritmic based on 'sample'
    returns reduced ndarrays
    """
    assert x.size == y.size, 'arrays must have same length, {}, {}'.format(
        x.size, y.size)
    per_sample = 3
    samples = int(y.size) / factor
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


def plot_middle(ax1, x, y, size, reduce):
    """ plots data for middle graphs"""
    ycore = abs(np.fft.fft(y))[:size]
    loglog(ax1, x[:size], ycore, reduce)
    # ax1.tick_params('y', colors='b')
    ax2 = ax1.twinx()
    semilogx(ax2, x[:size], np.sqrt(np.cumsum((ycore)**2)), reduce, 'r')
    # ax2.tick_params('y', colors='r')


# TODO: use reduce on x and y (remember to turn of sample step)
def plot_bottom(ax, x, y, heatmap, *args):
    """ plots data for bottom graphs"""
    if heatmap:
        plot_heatmap(ax, x, y)
    else:
        # x1, y1 = xyreduce(x, y, 'lin', 4096)
        # y2, x2 = xyreduce(y, x, 'lin', 4096)
        # ax.plot(np.append(x1, x2), np.append(y1, y2), *args)

        ax.plot(x, y, *args)


def plot_heatmap(ax, x, y):
    """generates a heatmap from data"""
    heatmap, xedges, yedges = np.histogram2d(x, y, bins=100)
    extent = [xedges[0], xedges[-1], yedges[0], yedges[-1]]
    thresh = 1
    # fill the areas with low density by NaNs
    heatmap[heatmap < thresh] = np.nan

    ax.imshow(heatmap.T, cmap='jet', extent=extent, origin='lower')
