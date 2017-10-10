#!/usr/bin/env python3

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
Export data from various formats (biosignals and features)
to an HDF5 file.

"""
import os
import sys
import argparse
import json
import jsonschema
import pkg_resources

from . import utilities_h5 as h5utils
from . import utilities_general as utils
from . import utilities_edf as edfutils
from . import utilities_empatica as empaticautils
from . import utilities_firstbeat as firstbeatutils
from . import utilities_mydarwin as mydarwinutils
from . import utilities_psg as psgutils
from . import utilities_shimmer as shimmerutils
from . import utilities_neurone as neuroneutils
from . import utilities_actigraph as actigraphutils

def export_hdf5(fname):
    """
    Export data defined in a configuration file to an HDF5 file.

    Arguments:
       - fname : full path to the configuration file

    Returns:
       - Nothing. All data is written to the HDF5 fle, the filename
         of which is specified in the configuration file.
    """
    # Map for data reading functions
    readerlist = {"edf"                     : {'function' : edfutils.read_edf_file,                      'reader_type' : 'signal'}, 
                  "edf_faros"               : {'function' : edfutils.read_faros,                         'reader_type' : 'signal'},
                  "mydarwin_ibi"            : {'function' : mydarwinutils.read_mydarwin_data_ibi,        'reader_type' : 'signal'},
                  "mydarwin_summary"        : {'function' : mydarwinutils.read_mydarwin_data_summary,    'reader_type' : 'signal'},
                  "empatica"                : {'function' : empaticautils.read_empatica,                 'reader_type' : 'signal'},
                  "bodyguard_features"      : {'function' : firstbeatutils.read_bodyguard_features,      'reader_type' : 'signal'},
                  "bodyguard_features_misc" : {'function' : firstbeatutils.read_bodyguard_features_misc, 'reader_type' : 'signal'},
                  "bodyguard_ibi"           : {'function' : firstbeatutils.read_bodyguard_ibi,           'reader_type' : 'signal'},
                  "bodyguard_acc"           : {'function' : firstbeatutils.read_bodyguard_acc,           'reader_type' : 'signal'},
                  "psg_hypnogram"           : {'function' : psgutils.read_hypnogram,                     'reader_type' : 'signal'},
                  "psg_arousal"             : {'function' : psgutils.read_arousal,                       'reader_type' : 'signal'},
                  "shimmer"                 : {'function' : shimmerutils.read_shimmer,                   'reader_type' : 'signal'},
                  "neurone"                 : {'function' : neuroneutils.read_neurone_data_hdf5,         'reader_type' : 'signal'},
                  "neurone_events"          : {'function' : neuroneutils.read_neurone_events_hdf5,       'reader_type' : 'events'},
                  "actigraph"               : {'function' : actigraphutils.read_actigraph,               'reader_type' : 'signal'},
                  "text"                    : {'function' : utils.read_text,                 'reader_type' : 'text'},
                  }

    config = load_json_file(fname)
    fname_out = config["output"]["filename"]

    print("Creating new HDF5 file:\t", fname_out, "\n\n")
    fid = h5utils.init_h5(fname_out)

    dataset_list = config["datasets"]

    for dataset in dataset_list:
        data = readerlist[dataset["data_type"]]['function'](dataset["filename"])

        if 'signal' == readerlist[dataset["data_type"]]['reader_type']:
            export_hdf5_signal(dataset, data, fid)
        if 'events' == readerlist[dataset["data_type"]]['reader_type']:
            export_hdf5_events(dataset, data, fid)
        if 'text' == readerlist[dataset["data_type"]]['reader_type']:
            export_hdf5_text(dataset, data, fid)

            
def export_hdf5_text(dataset, data, fid):
    """
    Write text data into an HDF5 file.

    Arguents:
       - dataset : a dictionary describing
                   the dataset to be exported
         
       - data : the data to be written

       - fid : file handle to the HDF5 file

    Returns:
       - Nothing
    """

    for dset_map in dataset["maps"]:
        print("Processing path:\t", dset_map["path"])
        
        h5utils.add_text_h5(fid,
                              dset_map["path"],
                              data = data['text'])

        if "meta" in dset_map.keys():
            h5utils.add_metadata_h5(fid,
                                    dset_map["path"],
                                    dset_map["meta"])

            
def export_hdf5_events(dataset, data, fid):
    """
    Write event data into an HDF5 file.

    Arguents:
       - dataset : a dictionary describing
                   the dataset to be exported
         
       - data : the data to be written

       - fid : file handle to the HDF5 file

    Returns:
       - Nothing
    """

    for dset_map in dataset["maps"]:
        print("Processing path:\t", dset_map["path"])
        
        h5utils.add_events_h5(fid,
                              dset_map["path"],
                              data = data['events'],
                              dtype = data['dtype'])

        if "meta" in dset_map.keys():
            h5utils.add_metadata_h5(fid,
                                    dset_map["path"],
                                    dset_map["meta"])

            
def export_hdf5_signal(dataset, data, fid):
    """
    Write signal data into an HDF5 file.

    Arguents:
       - dataset : a dictionary describing
                   the dataset to be exported
         
       - data : the data to be written

       - fid : file handle to the HDF5 file

    Returns:
       - Nothing
    """
    
    for dset_map in dataset["maps"]:
        print("Processing path:\t", dset_map["path"])

        if dset_map["channels"] == ["*"]:
            dset_map["channels"] = utils.get_channels_in_set(data)

        h5utils.add_data_h5(fid,
                            dset_map["path"],
                            data,
                            dset_map["channels"],
                            shared_group=dset_map["shared_group"])

        if "meta" in dset_map.keys():
            h5utils.add_metadata_h5(fid,
                                    dset_map["path"],
                                    dset_map["meta"],
                                    dset_map["channels"])

                
def load_json_file(fname):
    """
    Read the contents of a json file.

    Arguents:
       - fname : filename of the json file

    Returns:
       - The jason data as a dict.
    """
    out = None
    try:
        out = json.loads(open(fname, "r").read())
    except ValueError as e:
        print("\nError in JSON file!\nUnable to continue.")
        print("Error message below:\n")
        print("\t",e, "\n")
        sys.exit(1)
    return out

def validate_config(fname):
    """
    Validate configuration file in json format.
    """
    # Load schema
    schema_fname = pkg_resources.resource_filename('export2hdf5', "config_schema.json")
    schema = load_json_file(schema_fname)
    config = load_json_file(fname)

    res = None
    try:
        jsonschema.validate(config, schema)
    except jsonschema.ValidationError as e:
        res = e.message
    except jsonschema.SchemaError as e:
        res = e

    return res

def export2hdf5_cli():
    """
    Commmand line interface for export2hdf5.
    """
    parser = argparse.ArgumentParser(description="export2hdf5")
    parser.add_argument("--config",
                        dest="config_file",
                        help="Configuration file (in json-format).")
    parser.add_argument("--validate-only",
                        action="store_true",
                        dest="validate_only",
                        help="Just validate configuration file but do not process data.")

    args = parser.parse_args()

    if args.config_file is None:
        print("\nConfiguration file not given!\n")
        sys.exit(1)

    if not os.path.isfile(args.config_file):
        print("\nConfiguration file not found!\n")
        sys.exit(1)

    # Validate the input
    res = validate_config(args.config_file)

    if args.validate_only:
        if res is None:
            print("\nConfiguration file OK!\n")
        else:
            print("\nWarning! Errors in configuration file!\n")
            print(res)
        sys.exit(0)

    # Export data
    print("\nExporting data.\n")
    export_hdf5(args.config_file)

if __name__ == "__main__":
    export2hdf5_cli()
