""" example program to create a gain file for a signal generator setup """
from specanalyzer import EnetRandSFSP
from siggen import SignalGenerator

# setup signal generator
FREQ = 185.7 # frequency to run profile on
GEN_MIN = -30 # minimum signal generator output
GEN_MAX = 15 # maximun signal generator output
GEN_ADDR = ('131.243.171.52', 18) # spectrum analyzer address
ATTENUATION = 0 # attenuation between signal generator and spectrum analyzer

SPEC_SPAN = 10. # initial span of spectrum analyzer window
SPEC_ADDR = '131.243.171.57'


# Setup spectrum analyzer
spec = EnetRandSFSP(SPEC_ADDR, 18)

spec.reset() # not necessary if window manually set up
spec.disp_on(False)
spec.set_window(FREQ, SPEC_SPAN, GEN_MIN) # not necessary if window manually set up
spec.continuous_sweep(False)

# setup signal generator
gen = SignalGenerator(GEN_ADDR, min_output=GEN_MIN, max_output=GEN_MAX)
gen.freq(FREQ)


# Profile signal source. time in seconds ~= 4 * points * runs
gen.profile_gain('example_bnc845', lambda: spec.get_peak() - ATTENUATION, points=91, runs=3)
spec.continuous_sweep(True)
spec.disp_on(True)
