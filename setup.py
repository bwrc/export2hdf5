from setuptools import setup

setup(name='export2hdf5',
      version='1.0.3',
      description='Export data from various formats into an HDF5 file.',
      author='Andreas Henelius, Finnish Institute of Occupational Health',
      author_email='andreas.henelius@ttl.fi',
      url='https://github.com/bwrc/export2hdf5',
      license='MIT',
      packages=['export2hdf5'],
      package_dir={'export2hdf5': 'export2hdf5'},
      include_package_data=True,
      install_requires=['jsonschema',
                        'pyedflib',
                        'numpy',
                        'scipy',
                        'h5py'],
      entry_points={"console_scripts":
                    ["export2hdf = export2hdf5.export_hdf5:export2hdf5_cli"]})
