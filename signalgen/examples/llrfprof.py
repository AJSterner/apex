""" used to profile llrf """
import sys
import argparse

import numpy as np
from six.moves import input
from siggen import SignalGenerator

from adcutils import which_channel, gen_filename, adc_vals

GEN_ADDR = ('131.243.201.231', 18)
WAV_MIN = -30
WAV_MAX = 15
FREQ = 185.7
POINTS = 91
ROW_FORMAT = " ".join(["{" + str(i) + ":>10}" for i in range(3)]) + '\n'


def main(args):
    channel = which_channel()
    gain_file = None if args.profile else channel.gain_file
    gen = SignalGenerator(addr=GEN_ADDR, min_output=args.min, max_output=args.max, gain_file=gain_file)

    if args.profile:
        profile(gen, channel.gain_file)
        return

    inputs = np.linspace(args.min, args.max, num=args.points, endpoint=True)
    if inputs_ok(args.min, args.max) != 'Y':
        sys.exit(0)

    with open(gen_filename(channel.name), 'w+') as f:
        gen.power_sweep(inputs, output_callback, (channel.adc, f))

def output_callback(power_in, state):
    adc, f = state
    adc_min, adc_max = adc_vals(adc)
    print("In: {0:>.1}, Min: {1:>10}, Max: {2:>10}".format(power_in, adc_min, adc_max))
    f.write(ROW_FORMAT.format(power_in, adc_min, adc_max))   


def profile(gen, filename):
    from visainst import SpecAnalyzer
    spec = SpecAnalyzer()
    spec.set_window(FREQ, 10, gen.min_output)
    spec.continuous_sweep()

    if filename == "amp_gain":
        attn = -20
    else:
        attn = 0
    
    gen.profile_gain(filename, lambda: spec.get_peak() - attn, points=451)



def inputs_ok(low, high):
    print("Input Low: " + str(low) + "\nInput High: " +
          str(high))
    return input("Are these inputs ok? [Y/n]: ")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Profile llrf1")
    parser.add_argument("min", type=float, help="Min signal power (dbm)")
    parser.add_argument("max", type=float, help="Max signal power (dbm)")
    parser.add_argument("-p", "--points", type=int, help="Number of data points to take")
    parser.add_argument("--profile", help="Profile selected channel", action="store_true")
    args = parser.parse_args()
    main(args)
