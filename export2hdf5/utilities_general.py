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
This module contains some convenience functions for
handling datasets (lists containg the data from a
recording using some device.
"""

def get_channels_in_set(dataset):
    """
    Return list of all channels in the dataset.

    The dataset is a list, where each element
    represents a channel. Each channel is
    a dictionary of the form

    {"meta" : <dict with metadata>,
    "data" : {"time" : [...], "<channelname" : [...] }}

    """
    if not isinstance(dataset, list):
        dataset = [dataset]

    channels = []
    for ch_data in dataset:
        for ch_name in ch_data["data"].keys():
            if ch_name not in channels:
                channels += [ch_name]
    ind = channels.index("time")
    del channels[ind]
    return channels
