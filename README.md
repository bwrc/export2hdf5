Overview
--------
The `export2hdf5` programme is a utility for fusing multiple data sources into one HDF5 file. For instance, you might have simultaneously recorded physiological signals (e.g., multi-channel data) using several devices, each possibly having their own data format. To make the analysis of the combined data easier you can use `export2hdf5` to fuse all these recordings into one [HDF5](https://www.hdfgroup.org/) file.

You can also add metadata for each channel and decide how channels in the original recording are mapped to paths in the HDF5 file.


Installation
------------
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


Using export2hdf5
-----------------
The `export2hdf5` utility requires a configuration file in json-format. The configuration file specifies the filenames of the data sources. It is assumed that each data source has one or more channels, corresponding to different time series. For biomedical data the time series are typically different biosignals, e.g., brain signals recorded from different scalp locations or different ECG leads.

A sample configuration file is provided with export2hdf (`config_sample.json`). A short example with one three-channel recording is given below.

```json
{ "output" : {
    "filename" : "/tmp/example.h5"
},

  "datasets" : [

      { "filename" : "/path/to/the/recording.edf",
        "data_type" : "edf",
        "maps" : [
            { "path" : "ECG/Faros",
              "channels" : ["ECG_1", "ECG_2", "ECG_3"],
              "shared_group" : 1,
              "meta" : [
		  {"channels" : ["*"],
		   "info" : {"comment" : "default comment for all channels",
			     "comment2" : "another default comment for all channels"}
		  },
		  {"channels" : ["ECG_1"], 
                   "info" : {"comment" : "this is a comment for ECG1",
			     "example" : "this is a second comment for ECG1"}
		  },
		  {"channels" : ["ECG_2"],
		   "info" : {"example2" : "this is a comment for ECG2"}
		  }
              ]
            }
        ]
      }
]
}
```

In this example, *output* specifies the name of the HDF5 that is to be created. It it exists it will be overwritten.
Datasets are specified as elements in the 'datasets' list:

- filename : the filename of the data source
- maps : defines the mappings, i.e., mapping of channels in the data source to resources in the HDF5 file
- data_type : defines the type of data so that the correct import module can be used, see below for details on supported data formats
- shared_group : Boolean defining whether or not all of the channels in the current should share the same time vector. The channels can share the same time vector if they are sampled simultaneously at the same rate.
- meta : provide additional metadata.


Supported data types
--------------------
`export2hdf5` currently supports the following data formats:

- edf : data stored in the [European Data format](http://www.edfplus.info/)
- mydarwin : data exported from the [MyDarwin](www.mydarwin.eu) analysis platform
- empatica : data recorded using an [Empatica](https://www.empatica.com/) E4 device
- bodyguard_ibi : interbeat interval (IBI) data exported form the [Firstbeat](https://www.firstbeat.com/) Bodyguard platform
- bodyguard_acc : acceleration data exported form the FirstBeat Bodyguard platform
- bodyguard_features : features exported from the FirstBeat Bodyguard platform
- bodyguard_features_misc : more features exported from the FirstBeat Bodyguard platform
- hypnogram : hypnogram data in the [RemLogic](http://www.natus.com/index.cfm?page=products_1&crid=1014) XML format


Using export2hdf5
-----------------
To only validate that the given configuration file is OK:
```
export2hdf5 --config <path to config file> --validate-only
```

To fuse the data into an HDF5 file based on information in the configuration file:
```
export2hdf5 --config <path to config file>
```

License
-------
`export2hdf5` is licensed under the MIT license. Please see the file LICENSE for more details.
