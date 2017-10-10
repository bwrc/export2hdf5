# This file is part of export2hdf5
#
# Copyright 2017
# Andreas Henelius <andreas.henelius@ttl.fi>,
# Finnish Institute of Occupational Health
#
# This code is released under the MIT License
# http://opensource.org/licenses/mit-license.php
#
# Please see the file LICENSE for details.

"""
This module contains functions for reading data from the
Actigraph device (http://http://actigraphcorp.com).
The data must first be exported to CSV format.
"""

import io
import sys
from datetime import datetime, timedelta
import numpy as np

def read_actigraph(fname):
    """
    Read three-axis accelerometer data recorded using the actigraph.
    The sampling rate is 50 Hz.

    Arguments:
       - fname : the name of the file containing the data

    Returns:
       - a list of dictionaries, where each dictionary
         represents a feature as a time series ("signal")

    {"meta" : <dict with metadata>,
    "data" : {"time" : [...], "<channelname" : [...] }}

    """

    # Read the header
    header = []
    n_header = 11
    i = 0
    with open(fname, "r", encoding="utf-8") as file:
        for line in file:
            if i >= n_header:
                break
            header.append(line)
            i += 1
    
    # Extract the start date and time
    start_time = header[2].strip()[11:]
    start_date = header[3].strip()[11:]

    # Channel names
    channels = [i.strip() for i in header[10].split(",")]
    channels = [i.replace(" ", "_").lower() for i in channels]

    # Create the meta information
    meta = {}
   
    # Read the data
    # Reading depends on how many channels are present, i.e., on the data format (raw sampled at 50 Hz
    # or imu sampled at 100 Hz).
    if (len(channels) == 3):
        data = np.genfromtxt(fname, delimiter = ",", skip_header = 11, dtype = None)
        meta["sampling_rate"] = 50
    if (len(channels) == 11):
        data = np.genfromtxt(fname, delimiter = ",", skip_header = 11, dtype = None, usecols = range(1,11))
        channels = channels[1:]
        meta["sampling_rate"] = 100
    
    # Create a time vector for the data which has been sampled at 50Hz
    timevec = np.array(range(data.shape[0])) / meta["sampling_rate"]

    # Create the meta information
    meta["time_start"] = datetime.strptime(start_date + " " + start_time, "%d.%m.%Y %H:%M:%S")
    meta["time_stop"] = meta["time_start"] + timedelta(seconds = data.shape[0] / meta["sampling_rate"])
    
    # Put the data in a container

    out = [0] * data.shape[1]
    for i, label in enumerate(channels):
        data_out = {}
        data_out[label] = data[:,i]
        data_out["time"] = timevec
        out[i] = {"meta" : meta, "data" : data_out}

    return out
