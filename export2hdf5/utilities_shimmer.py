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

""" This module contains functions for readint data from a Shimmer device

http://www.shimmersensing.com/
"""

import datetime
import numpy as np

def read_shimmer(fname):
    """
    Read data recorded using a Shimmer device tored in csv format.

    Arguments:
       - fname : the name of the csv file

    Returns:

    A dictionary with the following format:

    {"meta" : <dict with metadata>,
    "data" : {"time" : [...], "<channelname" : [...] }}

    """
    fid = open(fname, "r")

    # Get the separator
    sep = fid.readline().split("=")[1].split('"')[0]

    # Get header and units
    header = [i.strip() for i in fid.readline().split(sep) if i.strip() != ""]
    device_id = "_".join(header[0].split("_")[0:2])
    header = [i.replace(device_id + "_", "") for i in header]
    header = [i.replace("_CAL", "") for i in header]
    header = [i.replace("_LN", "") for i in header]
    header = [i.replace("_A13", "") for i in header]

    # units = [i.strip() for i in fid.readline().split(sep) if i.strip() != ""]

    # Read the data
    data_tmp = np.genfromtxt(fname, delimiter=sep, skip_header=3)
    data_tmp = data_tmp[:, 0:10]

    # Store the data
    meta = {}
    data = {}

    # Convert the UNIX timestamp to seconds from milliseconds
    data_tmp[:, 0] = data_tmp[:, 0] / 1000

    # Create a time vector
    tvec = data_tmp[:, 0] - data_tmp[0, 0]

    # -- start time and sampling rate
    meta["time_start"] = datetime.datetime.fromtimestamp(float(data_tmp[0, 0]))
    meta["sampling_rate"] = 1 / (tvec[1] - tvec[0])

    data_tmp = data_tmp[:, 1:]
    header = header[1:]

    # -- the signals
    for ind, label in enumerate(header):
        data[label] = data_tmp[:, ind]

    return [{"data" : data, "meta" : meta}]
