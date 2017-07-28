""" contains methods to interface with signal generators """
import socket

DEFAULT_ADDRESS = ('131.243.201.231', 18)
MHZ = 1000000


class ValueSetException(Exception):
    """
    An instrument value couldn't be set. This usually happens when you set a
    value outside of the instruments range.
    """
    pass


class BNC845(object):
    """
    class which represents a BNC845 signal generator through a low-level socket connection
    (https://www.berkeleynucleonics.com/microwave-signal-generators)
    all methods will timeout after 10 seconds if communication can't be established
    """

    def __init__(self, address=DEFAULT_ADDRESS):
        self.addr = address
        self.sock = socket.create_connection(address, timeout=10)

    def identify(self):
        """ returns identification string of inst """
        return self.query('*IDN?\n')

    def query(self, msg):
        """
        sends string msg as utf-8 encoded bytes to instrument
        attempts to recieve a \n terminated string from instrument
        returns reply
        if msg is not \n terminated, \n is added
        """
        if msg[len(msg) - 1] != '\n':
            msg += '\n'
        self.send(msg)
        ret = self.recv(4096)
        while ret[len(ret) - 1] != '\n':
            ret += self.recv(4096)
        return ret

    def send(self, msg):
        """ sends string msg as utf-8 encoded bytes to instrument """
        self.sock.send(msg.encode())

    def recv(self, buff_size):
        """ returns buff_size number of bytes from instrument """
        return self.sock.recv(buff_size).decode('utf-8')

    def set_freq(self, new_freq, check=True):
        """
        sets frequency to freq (MHZ)
        if check is True then asks instrument if frequency was properly set
        Error to pass no frequency
        Raise ValueSetException if frequency could not be set
        """
        assert new_freq is not None
        self.send(':FREQ ' + str(new_freq) + 'MHZ\n')

        if check and abs(self.get_freq() / MHZ - new_freq) > 1E-5:
            raise ValueSetException(
                "Frequency could not be set {0:>.2}".format(new_freq))

    def get_freq(self):
        """ returns the frequency on the front panel of the instrument in MHZ """
        return float(self.query(':FREQ?'))

    def freq(self, new_freq=None):
        """
        if frequency given, sets frequency (MHZ)
        otherwise current frequency returned in MHZ
        """
        if new_freq is None:
            return self.get_freq()

        self.set_freq(new_freq, check=True)
        return new_freq

    def set_power(self, new_power, check=True):
        """
        set power to power in dbm
        if check is True then asks instrument if power was properly set
        Error to pass no power
        Raise ValueSetException if power could not be set
        """
        assert new_power is not None
        self.send(':POW ' + str(new_power) + '\n')

        if check and abs(self.get_power() - new_power) > 1E-5:
            raise ValueSetException(
                "Power could not be set {0:>.2}".format(new_power))

    def get_power(self):
        """ returns the power on the front panel of the instrument in dbm """
        return float(self.query(':POW?'))

    def power(self, new_power=None):
        """
        if power given, sets power (dbm)
        returns current power returned in dbm
        """
        if new_power is None:
            return self.get_power()
        self.set_power(new_power, check=True)

        return new_power

    def rf_on(self):
        """ Tells instrument to turn on rf signal """
        self.send(':OUTP ON\n')

    def rf_off(self):
        """ Tells instrument to turn off rf signal """
        self.send(':OUTP OFF\n')
