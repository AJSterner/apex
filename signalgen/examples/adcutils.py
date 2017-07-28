""" useful functions for adc measurements """

from time import localtime

from collections import namedtuple
Channel = namedtuple('Channel', ['name', 'adc', 'nominal', 'gain_file'])
CHANNELS = [Channel(name='Cavity Cell Voltage', adc='adc4', nominal=26, gain_file='amp_gain'),
            Channel(name='FWD Cavity', adc='adc2', nominal=15, gain_file='amp_gain'),
            Channel(name='REV Cavity', adc='adc3', nominal=15, gain_file='amp_gain'),
            Channel(name='Laser Cavity', adc='adc1', nominal=-27, gain_file='gen_gain')]


from epics import caget
from epics.ca import ChannelAccessException
try:
    if caget('llrf1:adc1_min') is None:
        raise Exception('Cannot connect to llrf1')
except ChannelAccessException as err:
    print('Cannot find EPICS CA DLL, make sure to set PATH')
    sys.exit(1)
except:
    raise

def adc_vals(channel):
    adc_min = caget('llrf1:' + channel + '_min')
    adc_max = caget('llrf1:' + channel + '_max')
    return adc_min, adc_max

def which_channel():
    for i, channel in enumerate(CHANNELS):
        print('[' + str(i) + '] ' + channel.name)
    try:
        channel = CHANNELS[int(input('Enter number of channel: '))]
    except ValueError:
        print('\nPlease enter a valid channel number')
        channel = which_channel()

    return channel

def gen_filename(prefix):
	""" generates filename: channel_name"""
    filename = prefix.replace(' ', '_')
    currtime = localtime()
    for i in range(5):
        filename += '-' + str(currtime[i])
    return filename