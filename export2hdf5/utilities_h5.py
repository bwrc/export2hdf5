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
This module contains helper functions for interacting with HDF5
file using the h5py module. The functions here allow

- creation of new HDF5 files
- creation of new groups in HDF5 files
- addition of metadata from a dict to objects in HDF5 files
- addition of signal data to a specific path in the HDF5 file,
  allowing the selection of data channels from a dataset
"""

import datetime
import h5py
from . import utilities_general as utils

def init_h5(fname):
    """ Open a HDF5 file and return handle to it. """
    return h5py.File(fname, "w")

def close_h5(fid):
    """ Close the HDF5 file with file handle fid. """
    fid.close()

def get_group(fid, path):
    """
    Get a handle to the group with the given path in the HDF5 file
    with handle fid, if the group exists, otherwise create it.
    """
    if path not in fid:
        grp = fid.create_group(path)
    else:
        grp = fid[path]
    return grp


def add_metadata(path, meta):
    """ Add the metadata in the dict meta to the HDF5 object obj. """
    for meta_tag in meta.keys():
        val = meta[meta_tag]

        if isinstance(val, datetime.datetime):
            val = val.strftime("%Y%m%dT%H%M%S")

        path.attrs[meta_tag] = val

def add_metadata_h5(fid, path, meta, channels):
    """
    Add the metadata contained in the dict 'meta' to the given path in
    the HDF5 file with handle fid.
    """
    print("\tSetting metadata")

    for group in meta:
        if ["*"] == group["channels"]:
            group["channels"] = channels
        for channel in group["channels"]:
            path_tmp = path + "/" + channel
            for attr in group["info"].keys():
                obj = get_group(fid, path_tmp)
                obj.attrs[attr] = group["info"][attr]

def add_data_h5(fid, path, dataset, channels, shared_group=True):
    """Add the channels in the dataset to the given path in the
    HDF5 file with handle fid.

    Arguments:
       - fid is the file handle to the HDF5 file

       - path is the base path inside the HDF5 file

       - dataset is a dict of dictionaries, each dictionary having the
         format:

           {"meta" : <dict with metadata>,
            "data" : {"time" : [...], "<channelname" : [...] }}

          and representing a channel.

    The boolean shared_group indicates whether all of the given
    channels should share the same time vector. The channels can share
    the same time vector if they are recorded in time synchrony and at
    the same sampling rate.

    """

    if shared_group:
        ## create the group
        grp = get_group(fid, path)

        ## add the metadata to the group
        metadata_added = False
        
        ## shared group, so all data vectors in the group share the
        ## same time vector
        timevector_added = False
        
        for i in dataset:
            channel = utils.get_channels_in_set(i)[0]
            path_tmp = path + "/" + channel

            if channel in channels:
                dset_d = fid.create_dataset(path_tmp,
                                            shape=i["data"][channel].shape,
                                            dtype="f",
                                            data=i["data"][channel])

                add_metadata(dset_d, i["meta"])

                if not timevector_added:
                    dset_t = fid.create_dataset(path + "/time",
                                                shape=i["data"]["time"].shape,
                                                dtype="f",
                                                data=i["data"]["time"])
                    timevector_added = True
                if not metadata_added:
                    add_metadata(grp, i["meta"])

    ## the group does not share the same time vector
    else:
        for i in dataset:
            channel = utils.get_channels_in_set(i)[0]
            if channel in channels:
                path_tmp = path + "/" + channel

                dset_d = fid.create_dataset(path_tmp + "/data",
                                            shape=i["data"][channel].shape,
                                            dtype="f",
                                            data=i["data"][channel])

                dset_t = fid.create_dataset(path_tmp + "/time",
                                            shape=i["data"]["time"].shape,
                                            dtype="f",
                                            data=i["data"]["time"])

                add_metadata(dset_d, i["meta"])

