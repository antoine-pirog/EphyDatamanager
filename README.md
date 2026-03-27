# Electrophysiology Datamanager

## Installation

1. Install a Python 3 virtual environment : `python3 -m venv .venv`
2. Activate virtual environment : 
  - UNIX : `source .venv/bin/active`
  - Windows : `.venv/Scripts/activate`
3. Clone repository : `git clone https://github.com/antoine-pirog/EphyDatamanager.git`
4. Change directory to repo root : `cd EphyDatamanager`
5. Install dependencies : `pip install -r requirements.txt`
6. Install library : `pip install -e .`

## Usage

Your usage will usually look like :

```python
from datamanager import manager as dm

""" Load ephy data """
data_path = "/path/to/data/supported_file.ext"  # Define data path
DS = dm.DataSource(data_path)                   # Instantiate data source
DS.load()                                       # Load data (depending on format : load headers only / load data into RAM)

""" Retrieve base information """
print("Available channels :", DS.getChannels()) # Read available channels
print("Sampling frequency :", DS.Fs, "Hz")      # Read sampling frequency

""" Retrieve samples for one channel """
channel_of_interest = "A-012"                   # Name of channel of interest (in human-frieldy format - here for Intan RHD2000 series)
signal = DS[channel_of_interest]                # Retrieve channel of interest in data source


```

See `examples/examples.ipynb` for extended usage examples.

### Using custom import parameters

Todo.