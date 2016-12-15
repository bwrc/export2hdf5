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
This module wraps some of the functions in pyedflib and provides
some convenience functions.
"""

import pyedflib
import numpy as np

def read_edf(fname):
    """Read EDF file with the name fname and returns an edf-object."""
    return pyedflib.EdfReader(fname)

def get_channel_list(edf):
    """ Return a list containing the channel names in the EDF file. """
    return edf.getSignalLabels()

def get_signal_header(edf, i):
    """ Read the signal header of the i:th signal in the edf file."""
    signal_header = edf.getSignalHeader(i)

    for k in signal_header.keys():
        if isinstance(signal_header[k], bytes):
            signal_header[k] = signal_header[k].decode("ASCII")

    return signal_header

def read_channel(edf, channel_name):
    """
    Read the channel with name channel_name from
    the edf file.
    """
    out = {}
    channel_list = get_channel_list(edf)

    try:
        i = channel_list.index(channel_name)
    except ValueError:
        print("Channel name not found in data")
        i = None

    if i is not None:
        out["data"] = edf.readSignal(i)
        out["properties"] = get_signal_header(edf, i)
        out["channel_name"] = channel_name
        out["properties"]["n_samples"] = len(out["data"])

    return out

def read_all_channels(edf):
    """
    Read all of the channels in the in the EDF file and return
    the data as a list.
    """
    out = []

    for channel_name in get_channel_list(edf):
        tmp = read_channel(edf, channel_name)
        if tmp:
            out += [tmp]

    return out

def get_starttime(edf):
    """ Return the startdate of the edf recording. """
    return edf.getHeader()["startdate"]

def print_channel_info(edf):
    """
    Print information (channel name and sampling rate) for
    each channel in the edf file.
    """
    channels = get_channel_list(edf)
    for i in range(len(channels)):
        tmp = get_signal_header(edf, i)
        print(tmp["transducer"], "\t", tmp["sample_rate"])

def read_edf_file(fname):
    """
    Read all channels in the EDF file and return the
    result as an array where where each element is a channel.
    Each channel is a dictionary:

    {"meta" : <dict with metadata>,
    "data" : {"time" : [...], "<channelname" : [...] }}

    """
    edf = read_edf(fname)
    channels = get_channel_list(edf)
    time_start = get_starttime(edf)
    out = [0] * len(channels)

    for i, channel in enumerate(channels):
        tmp = read_channel(edf, channel)

        meta = {}
        meta["time_start"] = time_start
        meta["sampling_rate"] = tmp["properties"]["sample_rate"]

        data = {}
        data[channel] = tmp["data"]
        data["time"] = np.arange(0, len(tmp["data"])) / meta["sampling_rate"]

        out[i] = {"data" : data, "meta" : meta}

    return out

def read_faros(fname):
    """
    Read all channels in the EDF file recorded using the Faros device 
    and return the result as an array where where each element is a channel.
    
    This function automatically converts accelerometer values
    from mG (milli G) to G.

    Each channel is a dictionary:

    {"meta" : <dict with metadata>,
    "data" : {"time" : [...], "<channelname" : [...] }}

    """
    res = read_edf_file(fname)

    # scale data from mG to G
    for i in range(len(res)):
        tmp = list(res[i]["data"].keys())
        del tmp[tmp.index("time")]
        channel = tmp[0]
        if channel[:-2] == "Accelerometer":
            print(channel)
            res[i]["data"][channel] = res[i]["data"][channel] / 1000
            
    return res
