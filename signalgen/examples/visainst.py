import visa

DEFAULT_CHANNEL = 16

def gpib_name(channel_no):
    """ returns a GPIB name string from channel_no """
    return 'GPIB0::' + str(channel_no) + '::INSTR'

class SpecAnalyzer(object):
    def __init__(self, channel_no=DEFAULT_CHANNEL):
        self.inst_name = gpib_name(channel_no)
        # TODO: check for inst
        rm = visa.ResourceManager()
        self.inst = rm.open_resource(self.inst_name, read_termination='\n')

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

    # def get_peak(self):
    #     """ only use after single sweep has been set """
    #     self.take_sweep()
    #     n_peaks = int(self.query('PEAKS TRB,TRA,FREQ?;'))
    #     assert n_peaks == 1, '{0:>5d}'.format(n_peaks)
    #     self.write('MKP TRB[1];')
    #     return self.marker_amp()

    # def get_peak_init(self):
    #     self.single_sweep()
    #     self.write('TH -60DM;')
