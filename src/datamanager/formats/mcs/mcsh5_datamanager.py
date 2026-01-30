import sys
import importlib.resources
from datamanager.manager import AbstractDataSource as DataSource

MCS_LIB_VERSIONS = [
    "Versions/McsPyDataTools040",
    "Versions/McsPyDataTools041",
    "Versions/McsPyDataTools042",
    "Versions/McsPyDataTools043",
]

class H5DataSource(DataSource):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    def getFs(self, i=0):
        self._checkDatatype()
        self._checkDataLoaded()
        r = self.import_parameters["recording_idx"]
        a = self.import_parameters["analog_stream_idx"]
        Fs = 1. * self.data.recordings[r].analog_streams[a].channel_infos[i].sampling_frequency.magnitude
        return Fs
    def _getSignal_formatspecific(self, i):
        r = self.import_parameters["recording_idx"]
        a = self.import_parameters["analog_stream_idx"]
        quantum = self.data.recordings[r].analog_streams[a].channel_infos[i].adc_step.to("microvolts").magnitude
        signal_i4 = self.data.recordings[r].analog_streams[a].channel_data[i,:]
        signal = quantum * signal_i4
        return signal
    def load(self):
        self._checkDatatype()
        # Cycle through format versions to find the right one
        print("MCS import - autoloading (cycling versions)")
        for mcsdata_lib_path in MCS_LIB_VERSIONS:
            try:
                import_path = importlib.resources.files("datamanager.formats.mcs").joinpath(mcsdata_lib_path)
                sys.path.insert(0, str(import_path))
                from McsPy.McsData import RawData as read_mcs
                self.data = read_mcs(self.file_path)
                print(f"  Success for {read_mcs}")
                break
            except AttributeError:
                sys.path.pop(0)
                print(f"  Failed for {read_mcs} (AttributeError)")
            except IOError:
                sys.path.pop(0)
                print(f"  Failed for {read_mcs} (IOError)")
            except:
                sys.path.pop(0)
                print(f"  Failed for {read_mcs} (Unexpected error)")
    def load_one_channel(self, i):
        print("Warning : loading one channel is not supported by current software. Regular loading instead.")
        self.load()
    def getChannels(self):
        self._checkDatatype()
        self._checkDataLoaded()
        rec_index    = self.import_parameters["recording_idx"]
        stream_index = self.import_parameters["analog_stream_idx"]
        analog_channels = self.data.recordings[rec_index].analog_streams[stream_index]
        COI_MCS = []
        for i,c in enumerate(analog_channels.channel_infos.values()):
            if not(c.label in COI_MCS):
                COI_MCS.append(c.label)
        return COI_MCS
    def _set_default_parameters_formatspecific(self):
        self.import_parameters["recording_idx"] = 0
        self.import_parameters["analog_stream_idx"] = 0
