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

""" This module contains functions for readint data from the
Empatica E4 device.

https://www.empatica.com/e4-wristband
"""

import glob
import datetime
import numpy as np

def read_empatica_ibi(fname, labels):
    """
    Read the IBI series from the Empatica csv file.
    The IBI data cannot be read using the read_empatica_gen
    function since the data header is slightly different.

    Arguments:
       - fname : the name of the csv file
       - labels : array containing the name that the
                  returned data will have

    Returns:

    A dictionary with the following format:

    {"meta" : <dict with metadata>,
    "data" : {"time" : [...], "<channelname" : [...] }}

    """
    header = open(fname, "r", encoding="utf-8").readlines()

    meta = {}
    data = {}

    t_start = header[0].split(",")[0].strip()
    meta["time_start"] = datetime.datetime.fromtimestamp(float(t_start))
    meta["sampling_rate"] = 0

    ## read the signal data and repack the data
    data_tmp = np.genfromtxt(fname, delimiter=",", skip_header=1)

    data[labels[0]] = data_tmp[:, 1] * 1000

    ## ceate a time vector for the data
    data["time"] = data_tmp[:, 0]

    return [{"data" : data, "meta" : meta}]

def read_empatica_gen(fname, labels, scalefactor = 1.0):
    """
    General function for reading signal data from
    an Empatica csv file.

    Arguments:
       - fname : the name of the csv file
       - labels : array containing the name that the
                  returned data will have

    The data is returned as a list with as many elements
    as there are channels in the data.

    The
    {"meta" : <dict with metadata>,
    "data" : {"time" : [...], "<channelname" : [...] }}

    """
    header = open(fname, "r", encoding="utf-8").readlines()

    meta = {}

    t_start = header[0].split(",")[0].strip()
    meta["time_start"] = datetime.datetime.fromtimestamp(float(t_start))
    meta["sampling_rate"] = float(header[1].split(",")[0].strip())

    data_tmp = np.genfromtxt(fname, delimiter=",", skip_header=2)

    out = [0] * len(labels)

    ## ceate a time vector for the data
    timevec = np.arange(0, len(data_tmp)) / meta["sampling_rate"]

    if len(labels) == 1:
        data = {}
        data[labels[0]] = data_tmp * scalefactor
        data["time"] = timevec
        out = [{"meta": meta, "data" : data}]
    else:
        for ind, lab in enumerate(labels):
            data = {}
            data[lab] = data_tmp[:, ind] * scalefactor
            data["time"] = timevec
            out[ind] = {"meta": meta, "data" : data}

    return out


def read_empatica(folder):
    """
    Read all channels from an an Empatica recording.

    Arguments:
        - folder: the folder containing the csv data files

    Returns:
        - A list where each element represent a channel.
          Each channel is a dictionary of the form:

    {"meta" : <dict with metadata>,
    "data" : {"time" : [...], "<channelname" : [...] }}

    The metadata contains at least the starting time as a datetime
    object and the sampling rate.

    """
    file_list = glob.glob(folder + "*.csv")
    out = []

    for i, f in enumerate(file_list):
        signal_type = f.split("/")[-1].replace(".csv", "")

        if signal_type == "ACC":
            out += read_empatica_gen(f, labels=["acc_x", "acc_y", "acc_z"], scalefactor = 1.0/64.0)
        if signal_type == "BVP":
            out += read_empatica_gen(f, labels=["BVP"])
        if signal_type == "EDA":
            out += read_empatica_gen(f, labels=["EDA"])
        if signal_type == "HR":
            out += read_empatica_gen(f, labels=["HR"])
        if signal_type == "TEMP":
            out += read_empatica_gen(f, labels=["temperature"])
        if signal_type == "IBI":
            out += read_empatica_ibi(f, labels=["IBI"])

    return out
