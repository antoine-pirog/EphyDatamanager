from ..manager import AbstractDataSource as DataSource

from . import myintanutil
from .load_intan_rhd_format import read_data as read_intan
from .load_intan_rhd_format_header_only import read_data as read_intan_header
from .load_intan_rhd_format_one_amp_channel import read_data as read_intan_one_channel

class IntanDataSource(DataSource):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    def getFs(self):
        self._checkDatatype()
        self._checkDataLoaded()
        Fs = 1. * self.data['frequency_parameters']['board_adc_sample_rate']
        return Fs
    def _getSignal_formatspecific(self, i):
        if not(self._isPartiallyLoaded()):
            signal = self.data['amplifier_data'][i]
        else:
            if (self.data["currently_loaded"]["channel"] != i):
                print("DataSource : Unloaded data requested ; auto-loading new data.")
                self.load_one_channel(i)
            signal = self.data['amplifier_data']
        return signal
    def load(self):
        self._checkDatatype()
        if not(self.import_parameters["is_huge"]):
            self.data = read_intan(self.file_path)
        else:
            self.data = read_intan_header(self.file_path)
            self.data["currently_loaded"] = {"channel": None}
    def load_one_channel(self, i):
        self.data = read_intan_one_channel(self.file_path, i)
        self.data["currently_loaded"] = {"channel": i}
    def getChannels(self):
        self._checkDatatype()
        self._checkDataLoaded()
        which = "custom_channel_name" if self.import_parameters["use_custom_names"] else "native_channel_name"
        channels = [chan[which] for chan in self.data['amplifier_channels']]
        return channels
    def _set_default_parameters_formatspecific(self):
        self.import_parameters["is_huge"]          = False
        self.import_parameters["use_custom_names"] = False
    # INTAN-SPECIFIC METHODS
    def _isPartiallyLoaded(self):
        self._checkDataLoaded()
        return ("currently_loaded" in self.data)