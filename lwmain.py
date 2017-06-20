""" produces useful graphs from provided ldump file """
import re
import sys
# import glob
# import os
# import time
import numpy as np
from matplotlib import pyplot as plt

import lwparse
import lwplot

FCLK = 1300e6 / 7.0 * 11 / 20
AVRFAC = 512

SAMPLE_STEP = 50

REDUCE1 = True
REDUCE2 = True
HEATMAP3 = False


def main(argv):
    """ produces useful graphs from given ldump file """
    filename = None

    if len(argv) >= 2:
        filename = argv[1]

    assert filename, "Filename must be provided!"

    filep = open(filename)
    scale = filep.read().split('\n')
    filep.close()

    wave_samp_per = int(re.match(r'# wave_samp_per is (\d*)', scale[1]).group(1))
    yscale = int(re.match(r'# yscale is (\d*)', scale[2]).group(1))


    tsamp = 1 / FCLK
    twave = (wave_samp_per / FCLK) * 22 * 2

    data = lwparse.parse(filename, yscale, AVRFAC)
    dsize = data['raw'][0].size

    print(wave_samp_per, tsamp, twave, twave * 1023, yscale, dsize)

    taxis = np.arange(dsize) * twave
    fwave = 1.0 / twave / dsize
    faxis = np.arange(dsize) * fwave
    plt.figure(1, figsize=(25, 19))
    plt.gca().ticklabel_format(useOffset=False)

    # plot first row
    for i in range(data['abs'].size):
        ax = plt.subplot(3, 4, i + 1)
        lwplot.plot(ax, taxis, data['abs'][i], REDUCE1, 'y')
        lwplot.plot(ax, taxis, data['avr'][i], REDUCE1, 'b')

    # plot second row
    # TODO: semilogx axis labels
    for i in range(data['abs'].size):
        ax = plt.subplot(3, 4, i + 5)
        lwplot.plot_middle(ax, faxis, data['abs'][i], dsize/2, REDUCE2)
        if i == 2:
            lwplot.plot_middle(
                ax, faxis, data['avr'][i][AVRFAC - 1:], dsize/2, REDUCE2)

    # plot third row
    for i in range(data['raw'].size):
        ax = plt.subplot(3, 4, i + 9)
        lwplot.plot_bottom(ax, data['raw'][i].real[::SAMPLE_STEP],
                           data['raw'][i].imag[::SAMPLE_STEP], HEATMAP3, '.')

    plt.suptitle(filename)
    plt.grid()

    plt.savefig(filename + '_grid.png')
    plt.figure(2)
    plt.plot(data['avr'][2][::SAMPLE_STEP], data['avr'][1][::SAMPLE_STEP])
    plt.suptitle(filename)

    # plt.show()
    plt.savefig(filename + '.png')


if __name__ == "__main__":
    main(sys.argv)
