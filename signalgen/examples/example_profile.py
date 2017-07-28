""" example program to create a gain file for a signal generator setup """
from visainst import SpecAnalyzer
from siggen import SignalGenerator

# setup signal generator
FREQ = 185.7 # frequency to run profile on
GEN_MIN = -30 # minimum signal generator output
GEN_MAX = 15 # maximun signal generator output
ADDRESS = ('131.243.201.231', 18) # spectrum analyzer address
ATTENUATION = 0 # attenuation between signal generator and spectrum analyzer

gen = SignalGenerator(ADDRESS, min_output=GEN_MIN, max_output=GEN_MAX)
gen.freq(FREQ)

# Setup spectrum analyzer
SPEC_SPAN = 10. # initial span of spectrum analyzer window
spec = SpecAnalyzer()
spec.set_window(FREQ, SPEC_SPAN, GEN_MIN)
spec.continuous_sweep()

# Profile signal source. time in seconds ~= 4 * points * runs
gen.profile_gain('test_gain_new', lambda: spec.get_peak() - ATTENUATION, points=10, runs=3)
