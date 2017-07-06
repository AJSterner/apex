# """ produces useful graphs from provided ldump file """
from __future__ import absolute_import
from __future__ import print_function
import re
import sys
# import glob
# import os
# import time
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt


import lwparse
import lwplot

FCLK = 1300e6 / 7.0 * 11 / 20
AVRFAC = 512
SAMPLE_STEP = 1

ROWS = 4
COLS = 4

REDUCE1 = True
REDUCE2 = True
HEATMAP3 = False

BOARDS = ['llrf1','llrf1molk1','llrf1molk2','llrf2molk1']


def main(argv):
    """ produces useful graphs from given ldump file """
    filename = None

    if len(argv) >= 2:
        filename = argv[1]

    assert filename, "Filename must be provided!"

    filep = open(filename)
    scale = filep.read().split('\n')
    filep.close()

    wave_samp_per = int(
        re.match(r'# wave_samp_per is (\d*)', scale[1]).group(1))
    yscale = int(re.match(r'# yscale is (\d*)', scale[2]).group(1))

    tsamp = 1 / FCLK
    twave = (wave_samp_per / FCLK) * 22 * 2

    data = lwparse.parse(filename, yscale, AVRFAC)
    dsize = data['raw'][0].size

    print(wave_samp_per, tsamp, twave, twave * 1023, yscale, dsize)

    taxis = np.arange(dsize) * twave
    fwave = 1.0 / twave / dsize
    faxis = np.arange(dsize) * fwave
    fig = plt.figure(1, figsize=(30, 20))
    plt.gca().ticklabel_format(useOffset=False)

    # plot first row
    for i in range(COLS):
        ax = plt.subplot(ROWS, COLS, i + 1)
        lwplot.plot(ax, taxis, data['abs'][i], REDUCE1, 'y')
        lwplot.plot(ax, taxis, data['avr'][i], REDUCE1, 'b')
        ax.set_title("Amplitude vs Time (" + BOARDS[i] + ")")
        ax.set_xlabel("Time (s)")
        ax.set_ylabel("Amplitude (% of FS)")

    # plot second row
    for i in range(COLS):
        ax = plt.subplot(ROWS, COLS, i + 5)
        # lwplot.plot_phase(ax, taxis, data['raw'][i], REDUCE2)
        z = data['raw'][i]
        y = np.unwrap(np.angle(z) - np.angle(z.mean()))
        lwplot.plot(ax, taxis, y, REDUCE2, 'y')
        lwplot.plot(ax, taxis, lwparse.moving_mean(y, AVRFAC), REDUCE2, 'b')
        ax.set_title("Phase vs Time (" + BOARDS[i] + ")")
        ax.set_xlabel("Time (s)")
        ax.set_ylabel("Phase (rad)")

    # plot third row
    for i in range(COLS):
        ax = plt.subplot(ROWS, COLS, i + 9)
        lwplot.plot_bottom(ax, data['raw'][i][::SAMPLE_STEP], HEATMAP3, '.')
        ax.set_title("Q vs I (" + BOARDS[i] + ")")
        ax.set_xlabel("I (au)")
        ax.set_ylabel("Q (au)")

    for i in range(COLS):
        ax = plt.subplot(ROWS, COLS, i + 13)
        lwplot.nplot_fft(ax, faxis, data['raw'][i], True)
        ax.set_title("Power Spectrum vs Frequency (" + BOARDS[i] + ")")
        ax.set_xlabel("Freq (Hz)")
        ax.set_ylabel("Power Spectrum (dbFS)")

    plt.suptitle(filename)
    # plt.grid()

    plt.savefig(filename + '_grid.png')
    plt.figure(2)
    plt.plot(data['avr'][2][::SAMPLE_STEP], data['avr'][1][::SAMPLE_STEP])
    plt.suptitle(filename)
    
    # fig.tight_layout()
    # plt.show()
    plt.savefig(filename + '.png')


if __name__ == "__main__":
    main(sys.argv)
