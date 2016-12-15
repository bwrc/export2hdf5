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
This module contains helper functions for extracting a hypnogram from an XML file.
"""

import xml.etree.ElementTree
from datetime import datetime
import numpy as np

def read_hypnogram(fname, events_accepted=["SLEEP-MT", "SLEEP-REM", "SLEEP-S0", "SLEEP-S1", "SLEEP-S2", "SLEEP-S3"]):
    """Extract a hypnogram from the  XML-file with filename fname.

    Arguments:
       - fname : the filename of the XML-file with the hypnogram
       - events_accepted : array of strings with the hypnogram events that are to be exported

    Returns:
        - The hypnogramas a dataset:

    {"meta" : <dict with metadata>,
    "data" : {"time" : [...], "<channelname" : [...] }}
    """

    res = read_psg_event(fname, events_accepted, check_consecutive=True)
    return hypnogram_to_dataset(res)

def read_arousal(fname, events_accepted=["AROUSAL"]):
    """Extract polysomnography (PSG) events from the  XML-file with filename fname.

    Arguments:
       - fname : the filename of the XML-file with the hypnogram
       - events_accepted : array of strings with the events that are to be exported

    Returns:
        - The events a dataset:

    {"meta" : <dict with metadata>,
    "data" : {"time" : [...], "<channelname" : [...] }}
    """

    res = read_psg_event(fname, events_accepted, check_consecutive=False)
    return psg_event_to_dataset(res)

def read_psg_event(fname, events_accepted, check_consecutive=False):
    """Read and extract events listed in the array events_accepted from
       the XML-file with filename fname.

    Arguments:
       - fname : the filename of the XML-file with the hypnogram
       - events_accepted : array of strings with the hypnogram events that are to be exported

    Returns:
        - The events as a dataset:

    {"meta" : <dict with metadata>,
    "data" : {"time" : [...], "<channelname" : [...] }}

    The events are exported from the time interval defined by the
    first occurrence of the LIGHTS_OFF event to the last occurrence of
    the event LIGHTS_ON.

    """

    timeformat = "%Y-%m-%dT%H:%M:%S.%f"

    docroot = xml.etree.ElementTree.parse(fname).getroot()
    events = docroot.findall("Events")[0].findall("Event")

    vec_t_start = []
    vec_t_stop = []
    vec_t_duration = []
    vec_t_type = []

    previous_event_start = None

    for e in events:
        ## parse event information
        ev_type = e.findall("Type")[0].text
        ev_start = e.findall("StartTime")[0].text
        ev_stop = e.findall("StopTime")[0].text

        ## event duration in milliseconds
        t_start = datetime.strptime(ev_start, timeformat)
        t_stop = datetime.strptime(ev_stop, timeformat)
        ev_duration = (t_stop - t_start).total_seconds() 

        ## create output string
        out = "{0:s}" + "\t" + "{1:s}" + "\t" + "{2:s}" + "\t" + "{3:f}"
        out = out.format(ev_type, ev_start, ev_stop, ev_duration)

        ## store and/or print event
        if ev_type in events_accepted:
            if check_consecutive:
                if previous_event_start is not None:
                    delta = (t_start - previous_event_start).total_seconds()
                    if delta != 30:
                        print("Error!\n\nConsecutive accepted events not spaced 30s apart.")
                previous_event_start = t_start

            vec_t_start += [t_start]
            vec_t_stop += [t_stop]
            vec_t_duration += [ev_duration]
            vec_t_type += [ev_type]

    res = {"t_start" : vec_t_start,
           "t_stop" : vec_t_stop,
           "duration" : vec_t_duration,
           "event_type" : vec_t_type,
           "n_events" : len(vec_t_start)}

    return res

def firstindex(x, val):
    """ Find the first index of val in the vector x. """
    try:
        return x.index(val)
    except ValueError:
        return 1

def lastindex(x, val):
    """ Find the last index of val in the vector x. """
    try:
        return len(x) - x[::-1].index(val) - 1
    except ValueError:
        return len(x)

def hypnogram_to_dataset(res):
    """Create a dataset from the hypnogram.

    A dataset is a list of dictionaries, each dictionary having the
    format:

    {"meta" : <dict with metadata>,
    "data" : {"time" : [...], "<channelname" : [...] }}
    """

    ## Find index of first "LIGHTS-ON" and last "LIGHTS-OFF"
    # i_start = firstindex(res["event_type"], "LIGHTS-OFF") + 1
    # i_stop = lastindex(res["event_type"], "LIGHTS-ON") - 1
    i_start = 0
    i_stop = len(res["event_type"])

    meta = {}
    data = {}

    hyp_val = {"SLEEP-MT"   : -1,
               "SLEEP-REM"  : -3,
               "SLEEP-S0"   : -2,
               "SLEEP-S1"   : -4,
               "SLEEP-S2"   : -5,
               "SLEEP-S3"   : -6,
               "LIGHTS-OFF" :  0,
               "LIGHTS-ON"  :  0}

    meta["time_start"] = res["t_start"][i_start:i_stop][0]
    meta["sampling_rate"] = 1.0 / 30.0

    data["hypnogram"] = np.array([hyp_val[i] for i in res["event_type"][i_start:i_stop]])
    data["time"] = np.arange(0, 30*len(data["hypnogram"]), step=30)

    return [{"meta" : meta, "data" : data}]


def psg_event_to_dataset(res):
    """Create a dataset from PSG events

    A dataset is a list of dictionaries, each dictionary having the
    format:

    {"meta" : <dict with metadata>,
    "data" : {"time" : [...], "<channelname" : [...] }}
    """

    meta = {}
    data = {}

    meta["time_start"] = res["t_start"][0]
    meta["sampling_rate"] = 0

    data["event"] = np.array([i for i in res["event_type"]])
    data["time"] = np.array([(i - res["t_start"][0]).total_seconds() for i in res["t_start"]])
    data["duration"] = res["duration"]

    return [{"meta" : meta, "data" : data}]
