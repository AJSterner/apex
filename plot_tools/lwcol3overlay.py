#lw3overlay.py
import re
import sys
import numpy as np
from matplotlib import pyplot as plt

import lwparse
import lwplot

AVRFAC = 512
FCLK = 1300e6 / 7.0 * 11 / 20

assert len(sys.argv) > 1, "You must provide at least one file"

# avr_data = []
# taxis = []

ax = plt.subplot(111)
for filename in sys.argv[1:]:
    filep = open(filename)
    scale = filep.read().split('\n')
    filep.close()

    wave_samp_per = int(re.match(r'# wave_samp_per is (\d*)', scale[1]).group(1))
    yscale = int(re.match(r'# yscale is (\d*)', scale[2]).group(1))

    data = lwparse.parse(filename, yscale, AVRFAC)
    taxis = (np.arange(data['avr'][2].size) * (wave_samp_per / FCLK) * 22 * 2)
    avr_data = data['avr'][2]

    lwplot.plot(ax, taxis, avr_data, True)

plt.show()