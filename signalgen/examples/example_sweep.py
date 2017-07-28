import numpy as np
from visainst import SpecAnalyzer
from siggen import SignalGenerator, sample_sweep_callback


FREQ = 185.7
SPAN = 10.
GEN_MIN = -30
GEN_MAX = 15
ADDRESS = ('131.243.201.231', 18)

# Setup spectrum analyzer
spec = SpecAnalyzer()
spec.set_window(FREQ, SPAN, GEN_MIN)
spec.continuous_sweep()

gen = SignalGenerator(ADDRESS, gain_file='test_gain_new')

inputs = np.linspace(gen.min_output, gen.max_output, num=91)
gen.power_sweep(inputs, sample_sweep_callback, spec.get_peak)
