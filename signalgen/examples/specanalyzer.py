from __future__ import print_function
import visa
from pyvisa.errors import VisaIOError

RM = visa.ResourceManager()

DEFAULT_CHANNEL = 16
# DEFAULT_ADDR = "TCPIP::131.243.171.57::1234::SOCKET"
DEFAULT_ADDR = "GPIB::18"

def gpib_addr_str(gpib_address):
    """ returns a GPIB name string from channel_no """
    return 'GPIB0::' + str(gpib_address) + '::INSTR'

class SpectrumAnalyzer(object):
    """ low level wrapper for visa controlled spectrum analyzers """
    def __init__(self, addr):
        self.addr = addr
        self.inst = RM.open_resource(addr)

    def write(self, message):
        self.inst.write(message)

    def read(self):
        return self.inst.read()

    def query(self, message, delay=None):
        return self.inst.query(message, delay=delay)

class RandSFSP(SpectrumAnalyzer):
    """
    wrapper fo F&S FSP spectrum analyzer visa library control
    
    Parameters
    ----------
    addr : string
        pyvisa address string.
        https://pyvisa.readthedocs.io/en/stable/names.html
    
    enet_gpib_addr : int, None
        gpib address if using prologix.biz gpib ethernet controller
    
    Returns
    -------
    RandSFSP spectrum analyzer object
    """
    def __init__(self, addr):
        super(RandSFSP, self).__init__(addr)
        self.inst.read_termination='\n'
        self.inst.timeout=15000

    def reset(self):
        """ resets device """
        self.write("*RST")
    
    def init_srq(self):
        """ sets ESE to 0x01 and SRE to 0x20 """
        self.write("*ESE 1;*WAI;*SRE 32")

    def set_window(self, freq, span, amp):
        """ sets window to given arguments """
        msg = "FREQ:CENT {0:.2f}MHz".format(freq)
        msg += ";*WAI;FREQ:SPAN {0:.2f}MHz".format(span)
        msg += ";*WAI;DISP:WIND:TRAC:Y:RLEV {0:.2f}dBm".format(amp)
        self.write(msg)

    def continuous_sweep(self, on=False):
        """ set single sweep mode """
        arg = "ON" if on else "OFF"
        self.write("INIT:CONT " + arg)
        self.sync_opc()

    def take_sweep(self):
        """ takes a single sweep and waits for completion """
        self.query("INIT;*OPC?")
        self.sync_opc()

    def peak_zoom(self):
        """ sets reference level to current marker power """
        self.write("CALC:MARK:FUNC:REF")
        self.sync_opc()

    def peak_power(self):
        """ returns peak power """
        power, opc = self.query("CALC:MARK:MAX;*WAI;CALC:MARK:Y?;*WAI;*OPC?", delay=0).split(';')
        assert int(opc) == 1
        return float(power)
    
    def get_peak(self):
        """ returns current peak power after adjusting reference level """
        self.auto_ref_lvl()
        return self.peak_power()

    def peak_frequency(self):
        """ returns the frequency of peak """
        try:
            freq = float(self.query("CALC:MARK:MAX;CALC:MARK:X?"))
            self.sync_opc()
        except VisaIOError:
            errno, errmsg = self.syst_err()
            print("F&P FSP Error {0}: {1}".format(errno, errmsg))
            raise

        return freq

    def disp_on(self, on=True):
        """ turns display on or off """
        arg = "ON" if on else "OFF"
        self.write("SYST:DISP:UPD " + arg)
        self.sync_opc()

    def auto_ref_lvl(self):
        """ runs the """
        self.write("SENS:POW:ACH:PRES:RLEV;*OPC?")
        assert int(self.read()) == 1

    def sync_opc(self):
        """ queries operation complete? """
        assert int(self.query("*OPC?")) == 1
    
    def syst_err(self):
        """ queries system err queue and returns result """
        err = self.query("SYST:ERR?")
        err = err.split(',')
        err_code = int(err[0])
        err_msg = str(err[1]).strip('"')
        return err_code, err_msg

class EnetRandSFSP(RandSFSP):
    """
    wrapper class for RandSFSP which allows it to be used over prologix.biz gpib ethernet controller

    Parameters
    ----------
    ip_addr : string
        ip address of prologix.biz controller.

    gpib_addr : int
        gpib address of instrument

    Returns
    -------
    RandSFSP spectrum analyzer object
    """
    def __init__(self, ip_addr, gpib_addr):
        super(EnetRandSFSP, self).__init__("TCPIP::" + ip_addr +"::1234::SOCKET")
        self.write("++mode 1\n++auto 1\n++addr {0:d}".format(gpib_addr))

class HP8593E(SpectrumAnalyzer):
    """ wrapper for HP8593H visa library control """
    def __init__(self, addr):
        super(HP8593E, self).__init__(addr, read_termination='\n')
        
    def write(self, msg):
        self.inst.write(msg)

    def read(self):
        return self.inst.read()

    def query(self, msg, fix_skipping=False):
        ret_msg = self.inst.query(msg)
        while fix_skipping and not ret_msg:
            ret_msg = self.inst.query(msg)
        return ret_msg

    def single_sweep(self):
        self.write('SNGLS;')

    def take_sweep(self):
        self.write('TS;')

    def set_window(self, freq, span, amp):
        assert amp < 30
        cmd_str = 'CF ' + str(freq) + ' MHZ;'
        cmd_str += 'SP ' + str(span) + ' MHZ;'
        cmd_str += 'RL' + str(amp) + 'DB;'
        self.write(cmd_str)

    def peak_zoom(self):
        self.write('PKZOOM 1MHZ')
        # Check peak zoom found peak
        ok = self.query('PKZMOK?;')
        assert int(ok) != 0

    def marker_amp(self):
        return float(self.query('MKA?;'))

    def peak(self):
        return self.marker_amp()

    def marker_freq(self):
        """ returns marker frequency in MHZ """
        return float(self.query('MKF?;'))/1E6


    def get_peak(self):
        self.peak_zoom()
        return self.peak()

    def continuous_sweep(self):
        self.write('CONT;')
