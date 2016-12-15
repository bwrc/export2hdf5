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

import re
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
    fid = open(fname, "r", encoding="utf-8")

    # Get the separator
    sep = fid.readline().split("=")[1].split('"')[0]

    # Get header and units
    header = [i.strip() for i in fid.readline().split(sep) if i.strip() != ""]
    header = fix_labels(header)
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

    # Preallocate structure to return
    out = [0] * len(header)

    # -- the signals
    for ind, label in enumerate(header):
        data = {}
        # Convert acceleration to units of g
        if re.search("Accel", label):
            data[label] = (data_tmp[:, ind] / 9.80665)
        else:
            data[label] = data_tmp[:, ind]
        data["time"] = tvec
        out[ind] = {"meta": meta, "data" : data}

    return out


def fix_labels(header):
    """
    Fix the labels from the Shimmer data by removing unnecessary
    text.

    Arguments:
       - header : the channel names as a list

    Returns:

    A list with the channel names fixed.

    """

    for i, label in enumerate(header):
        if re.search("Unix", label):
            header[i] = "Timestamp"
        if (re.search("Accel", label) and re.search("X", label)):
            header[i] = "Accel_X"
        if (re.search("Accel", label) and re.search("Y", label)):
            header[i] = "Accel_Y"
        if (re.search("Accel", label) and re.search("Z", label)):
            header[i] = "Accel_Z"
        if (re.search("Gyro", label) and re.search("X", label)):
            header[i] = "Gyro_X"
        if (re.search("Gyro", label) and re.search("Y", label)):
            header[i] = "Gyro_Y"
        if (re.search("Gyro", label) and re.search("Z", label)):
            header[i] = "Gyro_Z"
        if re.search("Pressure", label):
            header[i] = "Pressure"
        if re.search("Temp", label):
            header[i] = "Temperature"
        if re.search("GSR", label):
            header[i] = "GSR"

    return header
