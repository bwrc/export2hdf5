# Overview
The `export2hdf5` programme is a utility for fusing multiple data sources into one HDF5 file. For instance, you might have simultaneously recorded physiological signals (e.g., multi-channel data) using several devices, each possibly having their own data format. To make the analysis of the combined data easier you can use `export2hdf5` to fuse all these recordings into one [HDF5](https://www.hdfgroup.org/) file.

You can also add metadata for each channel and decide how channels in the original recording are mapped to paths in the HDF5 file.


# Installation
Please note that `export2hdf5` requires [Python 3](https://www.python.org/).

Using [PIP](https://github.com/pypa/pip) you can directly install the latest version of export2hdf as follows:
```bash
   pip3 install git+https://github.com/bwrc/export2hdf5
```
Please note that `export2hdf5` depends on (amongst other packages) [NumPy](http://www.numpy.org/) and [SciPy](https://www.scipy.org/) and you might want to install these separately using, e.g., your operating system package manager. In this case, install `export2hdf5` without dependencies as follows:
```bash
   pip3 install --no-dependencies git+https://github.com/bwrc/export2hdf5
```

`export2hdf5` is tested on GNU/Linux. On Linux you might have to use sudo for the installation.


# Using export2hdf5
The `export2hdf5` utility requires a configuration file in json-format. The configuration file specifies the filenames of the data sources. It is assumed that each data source has one or more channels, corresponding to different time series. For biomedical data the time series are typically different biosignals, e.g., brain signals recorded from different scalp locations or different ECG leads. Events can be discrete and are stored as a compouned HDF5 dataset.

A sample configuration file is provided with `export2hdf` (`config_sample.json`). A short example with one three-channel recording is given below.

```json
{
  "output": {
    "filename": "/tmp/example.h5"
  },
  "datasets": [
    {
      "filename": "/path/to/the/recording.edf",
      "data_type": "edf",
      "maps": [
        {
          "path": "ECG/Faros",
          "channels": [
            "ECG_1",
            "ECG_2",
            "ECG_3"
          ],
          "shared_group": 1,
          "meta": [
            {
              "channels": [
                "*"
              ],
              "info": {
                "comment": "default comment for all channels",
                "comment2": "another default comment for all channels"
              }
            },
            {
              "channels": [
                "ECG_1"
              ],
              "info": {
                "comment": "this is a comment for channel ECG_1",
                "example": "this is a second comment for ECG_2"
              }
            },
            {
              "channels": [
                "ECG_2"
              ],
              "info": {
                "example2": "this is a comment for ECG2"
              }
            }
          ]
        }
      ]
    }
  ]
}
```

In this example, `output` specifies the name of the HDF5 that is to be created. It it exists it will be overwritten.

`Datasets` are specified as elements in the 'datasets' list:

- `filename` : the filename of the data source
- `data_type` : defines the type of data so that the correct import module can be used, see below for details on supported data formats
- `maps` : defines the mappings, i.e., mapping of channels in the data source to resources in the HDF5 file. The `path` in the map gives the resource in the HDF5 file and the channels to be exported to this resource are given in the `channels` array. The wildcard `*` is supported and means all channels in the dataset, i.e., all channels in the file.
- `shared_group` : Boolean defining whether or not all of the channels in the current should share the same time vector. The channels can share the same time vector if they are sampled simultaneously at the same rate.
- `meta` : provide additional metadata. The metadata is given in structures containing information on which `channels` the metadata is relevant for. The wildcard `*` is supported and means all channels. The metadata (e.g., comments) are entered in the `info` section, in which different tags can be used (e.g., `comment` or `note`).

Exporting multiple groups from the same file to different groups in the HDF5 file is accomplished by adding multiple maps to one dataset, each map having a different path and a different set of channels (the channel sets can be overlapping in HDF5 resources). For instance, the (partial) configuration

```json
{ "filename" : "/path/to/embla.edf",
  "data_type" : "edf",
  "maps" : [
      { "path" : "EEG/Titanium",
        "channels" : ["M1", "M2", "E1", "E2", "Fz", "C3", "C4", "Oz"],
        "shared_group" : 1
      },
      { "path" : "EMG/Titanium",
        "channels" :  ["ChinL", "ChinR"],
        "shared_group" : 1
      }
  ]
}
```
places the EEG channels in the HDF5 resource `EEG/Titanium` and the EMG channels in the resource `EMG/Titanium`.


Note that for events (`neurone_events` currently the only event type) only `path` should be given in `maps`. An example is given next.

```json
{
  "filename": "/path/to/the/neurone/recording/",
  "data_type": "neurone_events",
  "maps": [
    {
      "path": "Events/Neurone"
    }
  ]
}
```

Text notes can also be stored as follows.

```json
{
  "filename": "/path/to/a/text/file.txt",
  "data_type": "text",
  "maps": [
    {
      "path": "Notes/Note_1"
    }
  ]
}
```

## Using export2hdf5 as a module from Python
The `export2hdf5` utility can also be used a module from Python, e.g., for automation of data export. Below is a brief example of how `export2hdf5` can be called from Python. Please note that `export2hdf5` requires [Python 3](https://www.python.org/).

```python
from export2hdf5 import export_hdf5

# define the configuration file
config_file = "config_example.json"

# validate the configuration file
config_check = export_hdf5.validate_config(config_file)

if config_check is None:
    print("Configuration file OK.")

# export data
export_hdf5.export_hdf5(config_file)
```


# Supported data types
`export2hdf5` currently supports the following data formats:

- `edf` : data stored in the [European Data format](http://www.edfplus.info/)
- `edf_faros` : data recoreded using the [Mega Electronics Ltd](http://www.megaemg.com) Faros device. The data is stored in the EDF. This function automatically converts accelerometer units to G from mG.
- `mydarwin_ibi` : IBI data exported from the [MyDarwin](www.mydarwin.eu) analysis platform
- `mydarwin_summary` : Summary data exported from the [MyDarwin](www.mydarwin.eu) analysis platform
- `empatica` : data recorded using an [Empatica](https://www.empatica.com/) E4 device
- `shimmer` : data recorded using a [Shimmer](https://www.shimmersensing.com/) device
- `bodyguard_ibi` : interbeat interval (IBI) data exported form the [Firstbeat](https://www.firstbeat.com/) Bodyguard platform
- `bodyguard_acc` : acceleration data exported form the FirstBeat Bodyguard platform
- `bodyguard_features` : features exported from the FirstBeat Bodyguard platform
- `bodyguard_features_misc` : more features exported from the FirstBeat Bodyguard platform
- `psg_hypnogram` : hypnogram data in the [RemLogic](http://www.natus.com/index.cfm?page=products_1&crid=1014) XML format
- `psg_arousal` : arousal events in the [RemLogic](http://www.natus.com/index.cfm?page=products_1&crid=1014) XML format
- `neurone` : data recorded using an [Bittium NeurOne](https://www.bittium.com/products_services/medical/bittium_neurone) device.
- `neurone_events` : events from data recorded using an [Bittium NeurOne](https://www.bittium.com/products_services/medical/bittium_neurone) device.
- `actigraph` : data recorded using an [ActiGraph](http://actigraphcorp.com/products-showcase/activity-monitors/actigraph-link/) device. The data must be exported to CSV format. Both 3-axis accelerometer data sampled at 50 Hz and raw data (accelerometer, gyroscope, magnetometer, temperature) data sampled at 100 Hz is supported.
- `text` : general text (UTF-8), e.g., notes.

# Using export2hdf5
To only validate that the given configuration file is OK:
```
export2hdf5 --config <path to config file> --validate-only
```

To fuse the data into an HDF5 file based on information in the configuration file:
```
export2hdf5 --config <path to config file>
```
This produces an HDF5 file in the location configured in the `output` section of the configuration file. All files are read from the locations specified in the locations specified in the `datasets` section in the configuration file.

# Reading HDF5 -files in other programming languages
## Python
```python
# load library
import h5py
import numpy as np

# get file handle
with h5py.File('/path/to/example.hdf5','r') as h5_file:
    # list groups in the file
    groups = list(h5_file.keys())
    print(groups)

    # read EEG data from one channel
    data = h5_file["/EEG/Device/Fz"]
```

## R
It is recommended to use the
[`rhdf5`-package](http://bioconductor.org/packages/release/bioc/html/rhdf5.html)
which supports compound datasets. See the link for installation
instructions.

```R
## load library
require(rhdf5)

## define filename
h5_file <- '/path/to/example.hdf5'

## list contents of file
rhdf5::h5ls(h5_file)

## read EEG data from one channel
data <- rhdf5::h5read(h5_file, '/EEG/Device/Fz')
```

## MATLAB
[MATLAB](https://www.mathworks.com/products/matlab.html) supports readng of HDF5-files without additional toolboxes.

```Matlab
% define filename
h5_file = '/path/to/example.hdf5'

% list contents of file
hi = h5info(h5_file)
h5disp(h5_file)
h5disp(h5_file, '/EEG/Device/T8')

% read EEG data from one channel
data = h5read(h5_file, '/EEG/Device/Fz')
```

# License
`export2hdf5` is licensed under the MIT license. Please see the file LICENSE for more details.
