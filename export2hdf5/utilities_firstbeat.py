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
This module contains functions for reading data from the
Firstbeat Bodyguard device. THe data is in the SDF format.
"""

import io
import sys
from datetime import datetime
import numpy as np

def read_bodyguard_features_misc(fname, time_start=""):
    """
    Read miscellaneous features exported from the Firstbeat analysis
    programme.

    Arguments:
       - fname : the name of the file containing the data
       - time_start : The starting time of the recording (str)
         The startimg time is not contained in the file.

    Returns:
       - a list of dictionaries, where each dictionary
         represents a feature as a time series ("signal")

    {"meta" : <dict with metadata>,
    "data" : {"time" : [...], "<channelname" : [...] }}

    """
    ## Read header of misc vectors
    tmp = open(fname, "r", encoding="utf-8")
    for i, line in enumerate(tmp):
        if i == 3:
            labels = [x.strip().replace("Vector", "") for x in line.split(";")]

    labels[2] = "time"

    ## Read the misc vectors
    tmp.seek(0)
    tmp_data = tmp.read().replace(",", ".")
    tmp.close()
    features = np.genfromtxt(io.BytesIO(tmp_data.encode()), delimiter=";", skip_header=4)

    ## get the entire cumulative time vector and then remove it from the main data
    timevec = features[:, 2]
    features = np.delete(features, 2, 1)
    del labels[2]

    ## create the metadata
    meta = {}

    ## create output as array since the sampling rate is different for different channels
    out = [0] * len(labels)

    meta["time_start"] = time_start
    meta["sampling_rate"] = 0

    for i, label in enumerate(labels):
        data = {}
        ind = np.isnan(features[:, i])

        data["time"] = timevec[np.logical_not(ind)]
        data[label] = features[np.logical_not(ind), i]

        out[i] = {"data" : data, "meta" : meta}

    return out

def read_bodyguard_features(fname):
    """
    Read features exported from the Firstbeat analysis
    programme.

    Arguments:
       - fname : the name of the file containing the data

    Returns:
       - a list of dictionaries, where each dictionary
         represents a feature as a time series ("signal")

    {"meta" : <dict with metadata>,
    "data" : {"time" : [...], "<channelname" : [...] }}

    """
    tmp = open(fname, "r", encoding="utf-8")

    meta = {}

    tmp_start_date = ''
    tmp_start_time = ''
    timeformat = "%d.%m.%Y %H:%M:%S"

    # Get the start time and the index where the data begins
    # Read data until we encounter the word "VECTORS", where
    # the data starts
    for i, line in enumerate(tmp):
        if line.startswith('SessionStartDate'):
            tmp_start_date = line.split(";")[1]
        if line.startswith('SessionStartTime'):
            tmp_start_time = line.split(";")[1]
        if line.strip() == "VECTORS":
            break

    time_start = tmp_start_date + " " + tmp_start_time
    meta["time_start"] = datetime.strptime(time_start, timeformat)
    meta["sampling_rate"] = 1

    ## Read the names of the vectors
    labels = tmp.readlines(1)[0]
    labels = labels.split(";")

    tmp.seek(0)
    tmp_data = tmp.read().replace(",", ".")
    tmp.close()

    ## Read the data and prepare the time vector
    ## Note! Uses the variable i from the for-loop over tmp above.
    features = np.genfromtxt(io.BytesIO(tmp_data.encode()), delimiter=";", skip_header=(i + 2))

    timevec = features[:, 0]
    features = np.delete(features, 0, 1) ## delete the cumulative seconds column
    features = np.delete(features, 0, 1) ## delete the time column
    labels = labels[2:]
    labels = [lab.strip().replace("Vector", "") for lab in labels]

    out = [0] * len(labels)

    for i, label in enumerate(labels):
        data = {}
        data["time"] = timevec
        data[label] = features[:, i]
        out[i] = {"meta" : meta, "data" : data}

    return out

def read_bodyguard_acc(fname):
    """
    Read Bodyguard acceleration data.

    Arguments:
       - fname : the name of the file containing the data

    Returns:
       - a list of dictionaries, where each dictionary
         contains the channel data.

    {"meta" : <dict with metadata>,
    "data" : {"time" : [...], "<channelname" : [...] }}

    """

    timeformat = "%d.%m.%Y %H:%M.%S"

    ## Containers
    meta = {}

    ## Read the header
    tmp = open(fname, "r", encoding="utf-8").readlines()
    header = tmp[0:5]

    meta["time_start"] = datetime.strptime(header[0].split(";")[1].strip(), timeformat)
    meta["sampling_rate"] = float(header[2].split(";")[1].strip().replace("Hz", ""))

    gscale = header[1].split(";")[1].strip()
    samplesize = header[3].split(";")[1].strip()

    if not (("4G" == gscale) and ("8bit" == samplesize)):
        print("Warning!\nIncompatible gscale and/or samplesize!\n\n")
        sys.exit(1)

    ## Read the signals
    data_tmp = np.genfromtxt(fname, delimiter=";", skip_header=5)

    ## Pack signals and data
    out = [0] * 3
    labels = ["acc_x", "acc_y", "acc_z"]

    ## Divide data by 32 to scale to g-values (assuming 4g range and 8-bit resolution)
    ## Divide the time values by 1000 to convert to seconds from milliseconds.
    for i, lab in enumerate(labels):
        data = {}
        data["time"] = data_tmp[:, 0] / 1000.0
        data[lab] = data_tmp[:, (i+1)] / 32

        out[i] = {"meta" : meta, "data" : data}

    return out

def read_bodyguard_ibi(fname):
    """
    Read Bodyguard interbeat interval (IBI)  data.

    Arguments:
       - fname : the name of the file containing the data

    Returns:
       - a list of dictionaries, where each dictionary
         contains the channel data.

    {"meta" : <dict with metadata>,
    "data" : {"time" : [...], "<channelname" : [...] }}

    """

    ## Read the header
    header = open(fname, "r", encoding="utf-8").readlines()

    timeformat = "%d.%m.%Y %H:%M:%S"

    meta = {}

    labels = [i.strip().replace("Vector", "") for i in header[4].split(";")]

    time_start = [i.strip() for i in header[1].split(":")[1:]]
    time_start = time_start[0] + ":" + time_start[1] + ":" + time_start[2]
    meta["time_start"] = datetime.strptime(time_start, timeformat)
    meta["sampling_rate"] = 0

    data_tmp = np.genfromtxt(fname, delimiter=";", skip_header=5)
    ind = np.isnan(data_tmp[:, 0])

    out = [0] * len(labels)

    timevec = np.concatenate(([0], np.cumsum(data_tmp[np.logical_not(ind), 0] / 1000)))
    timevec = timevec[0:-1]

    for i, lab in enumerate(labels):
        data = {}
        data[lab] = data_tmp[np.logical_not(ind), i]
        data["time"] = timevec
        out[i] = {"meta" : meta, "data" : data}

    return out
