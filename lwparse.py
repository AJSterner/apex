""" provides a function to parse data from ldump into useful format """
import numpy as np
import pandas as pd


def parse(filename, yscale, avrfac):
    """
    parse ldump file to a lib object containing raw data (complex), absolute values
    of data and a moving average with window of avrfac. Data is scaled using yscale
    """
    data = pd.read_csv(filename, skiprows=4, sep=' ', names=range(
        8), na_values='#', dtype=np.float, engine='c')
    data = data.dropna()

    raw_data = np.empty(4, dtype=np.ndarray)
    abs_data = np.empty(4, dtype=np.ndarray)
    avr_data = np.empty(4, dtype=np.ndarray)
    for i in range(4):
        raw_data[i] = (np.array(data[i * 2]) + 1j *
                       np.array(data[i * 2 + 1])) / yscale
        abs_data[i] = abs(raw_data[i])
        avr_data[i] = np.array(pd.Series(abs_data[i]).rolling(
            window=avrfac, center=False).mean())
    return {'raw': raw_data, 'abs': abs_data, 'avr': avr_data}
