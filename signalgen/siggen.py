""" contains a generic signal generator class """

from __future__ import print_function
from time import sleep
import numpy as np
from scipy.interpolate import interp1d

from bncinst import BNC845

DEFAULT_MIN = -30.0
DEFAULT_MAX = 15.0
DEFAULT_ADDRESS = ('131.243.201.231', 18)

class SignalGenerator(object):
    """
    Represents a signal generator. Provides methods to interface with the signal generator at
    a higher level.

    This representation includes support for using 'gain files' which map 'panel power outputs'
    (powers that a signal generator thinks it's outputting) to the gain at that panel power output.
    When a gain file is specified, every power that the user sees is 'real power output' which is
    then translated to 'panel power output' to be sent to the signal generator

    WARNING: these maps are approximate (especially with unstable signals) USE AT YOUR OWN RISK

    TODO: make signal generator generic. Currently only works with BNC845 class.

    Parameters
    ----------
    addr : tuple ('ip.address', port), optional
        address tuple to be passed to socket

    min_output : optional
        minimum real power output that the signal generator is allowed to output.
        If None, default bounds are used

    max_output : optional
        maximum real power output that the signal generator is allowed to output.
        If None, default bounds are used

    gain_file : str, optional
        name of the gain file to use

    Returns
    -------
    SignalGenerator object
    """
    def __init__(self, addr=DEFAULT_ADDRESS, min_output=None, max_output=None, gain_file=None):
        # initialize signal generator
        self.gen = BNC845(addr)
        self.gain_file = gain_file

        if self.gain_file:
            panels, gains = np.loadtxt(self.gain_file, unpack=True)
            self.panel_to_real_func = interp1d(panels, panels + gains)
            self.real_to_panel_func = interp1d(panels + gains, panels)
            self.min_output = min_output if min_output else panels[0] + gains[0]
            self.max_output = max_output if max_output else panels[-1] + gains[-1]
        else:
            self.min_output = min_output if min_output else DEFAULT_MIN
            self.max_output = max_output if max_output else DEFAULT_MAX

    def identify(self):
        """ Returns the instrument identification string """
        return self.gen.identify()

    def freq(self, new_freq=None):
        """
        sets the signal frequency to new_freq if given
        returns the current frequency
        """
        return self.gen.freq(new_freq)

    def power(self, new_power=None):
        """
        sets the real output power to new_power if given
        returns the current real output power
        """
        if new_power and self.gain_file:
            new_power = self.real_to_panel(new_power)
        return self.gen.power(new_power)

    def power_sweep(self, out_powers, callback, state=None):
        """
        sets the power to each power in out_powers in order calling callback with each set power

        Parameters
        ----------
        out_powers : iterable
            the output powers to use
        callback : function(power, state)
            called on each set power with power and state as arguments
        state :
            passed to callback on each set power
        """
        self.rf_off()
        self.power(out_powers[0])
        try:
            self.rf_on()
            sleep(1)
            for power in out_powers:
                self.power(power)
                callback(power, state)
        except:
            self.rf_off()
            raise

        self.rf_off()

    def rf_on(self):
        """ turns rf signal on (begins signal output) """
        self.gen.rf_on()

    def rf_off(self):
        """ turns rf signal off (ends signal output) """
        self.gen.rf_off()

    def panel_to_real(self, panel_power):
        """ returns real output from panel output """
        assert self.gain_file, "Gain file must be provided"
        return self.panel_to_real_func(panel_power)

    def real_to_panel(self, real_power):
        """ returns panel power from real power """
        assert self.gain_file, "Gain file must be provided"
        return self.real_to_panel_func(real_power)

    def profile_gain(self, filename, real_power, points=91):
        """
        creates a gain file for current setup
        There must not be a current gain file
        NOTES: I think runtime = ~ 2seconds/point

        Parameters
        ----------
        filename : str
            name of file to write
        real_power : function
            function called without arguments which returns the current real power output
            (eg. spectrum analyzer output)
        points : int, optional
            number of data points to take
        """
        assert self.gain_file is None, "cannot profile signal generator with a current gain file"
        with open(filename, 'w+') as gain_file:
            outputs = np.linspace(self.min_output, self.max_output, num=points, endpoint=True)
            self.power_sweep(outputs, profile_gain_callback, (gain_file, real_power()))

def profile_gain_callback(panel_out, state):
    """ helper function used with profile_gain """
    gain_file, real_power = state
    real_out = real_power()
    print("Panel output: {0:>.3f}, Real output: {1:>.3f}, Gain: {2:>.3f}".format(panel_out, real_out, real_out - panel_out))
    gain_file.write("{0:>10f} {1:>10f}\n".format(panel_out, real_out - panel_out))

def sample_sweep_callback(power_out, state):
    """ when used with power sweep, outputs the input power and the measured gain"""
    real_power = state
    print("Input power: {0:>.3f}dbm, Measured gain: {1:>.3f}dbm".format(power_out, power_out - real_power()))
