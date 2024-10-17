from ..manager import AbstractDataSource as DataSource

from .read_data import read_bin_multichannel, read_bin_singlechannel

class BinDataSource(DataSource):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    def getFs(self):
        self._checkDatatype()
        self._checkDataLoaded()
        return self.data['Fs']
    def _getSignal_formatspecific(self, i):
        return self.data['data'][:, i]
    def load(self):
        self._check_import_parameters()
        self.data = read_bin_multichannel(
            filepath    = self.file_path, 
            quantum     = self.import_parameters['quantum'],
            Fs          = self.import_parameters['Fs'],
            N_channels  = self.import_parameters['Nchannels'],
            data_format = self.import_parameters['data_format']
        )
    def load_one_channel(self, i):
        self._check_import_parameters()
        self.data = read_bin_singlechannel(
            filepath    = self.file_path, 
            ch          = i,
            quantum     = self.import_parameters['quantum'],
            Fs          = self.import_parameters['Fs'],
            N_channels  = self.import_parameters['Nchannels'],
            data_format = self.import_parameters['data_format']
        )
        self.data["currently_loaded"] = {"channel": i}
    def getChannels(self):
        return [i for i in range(self.import_parameters['Nchannels'])]
    def _set_default_parameters_formatspecific(self):
        self.import_parameters["quantum"] = 1
        self.import_parameters["Nchannels"] = 64
        self.import_parameters["Fs"] = 10_000
        self.import_parameters["data_format"] = ">h"
        self.import_parameters["is_huge"] = False #TODO
    def _check_import_parameters(self):
        if self.import_parameters["quantum"] == 1:
            print("Warning : quantum is set to 1. Loaded data will reflect raw A/D values, not Voltage.")
    # INTAN-SPECIFIC METHODS
    def _isPartiallyLoaded(self):
        self._checkDataLoaded()
        return ("currently_loaded" in self.data)
