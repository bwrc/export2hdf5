# This file is part of export2hdf5
#
# Copyright 2016
# Andreas Henelius <andreas.henelius@ttl.fi>,
# Finnish Institute of Occupational Health
#
# This code is released under the MIT License
# http://opensource.org/licenses/mit-license.php
#
# Please see the file LICENSE for details.

"""
This module contains functions for reading
data exported from MyDarwin in csv format.
"""

import numpy as np

def read_mydarwin_data_ibi(fname):
    """
    Read interbeat interval (IBI) data in csv
    format exported from MyDarwin contained in
    the file with the name fname.

    Arguments:
       - fname : file name

    Returns:
       - A list with a dictionary of the form

         {"meta" : <dict with metadata>,
          "data" : {"time" : [...], "<channelname" : [...] }}

    Notes:

       - The metadata contains no starting time as this is not
         present in the file. The sampling rate is 0 since it
         is irregular.
    """

    meta = {}
    data = {}

    meta["time_start"] = ''
    meta["sampling_rate"] = 0


    data_tmp = np.genfromtxt(fname, delimiter=",", skip_header=0)

    data["time"] = np.cumsum(data_tmp[:, 0] / 1000)
    data["ibi"] = data_tmp[:, 0]
    data["beat_type"] = data_tmp[:, 1]

    return [{"meta" : meta, "data" : data}]


def read_mydarwin_data_summary(fname):
    """
    Read data in csv format exported
    from MyDarwin contained in the file
    with the name fname.

    Arguments:
       - fname : file name

    Returns:
       - A list with a dictionary of the form

         {"meta" : <dict with metadata>,
          "data" : {"time" : [...], "<channelname" : [...] }}

    Notes:

       - The metadata contains no starting time as this is not
         present in the file. The sampling rate is 0 since it
         is irregular.
    """


    data_tmp = np.genfromtxt(fname, delimiter=",", skip_header=0, names = True)

    labels = data_tmp.dtype.names
    
    skip_columns = ["start", "end"]

    meta = {}
    meta["time_start"] = ''
    meta["sampling_rate"] = 0

    timevec = data_tmp["start"]

    out = [0] * len(labels)
    
    i = 0
    for label in labels:
        if label not in skip_columns:
            data = {}

            data["time"] = timevec
            data[label] = data_tmp[label]

            out[i] = {"data" : data, "meta" : meta}
            i += 1

    return out

