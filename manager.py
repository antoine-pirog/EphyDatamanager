from .intan.load_intan_rhd_format import read_data as read_intan
from .intan.load_intan_rhd_format_header_only import read_data as read_intan_header
from .intan.load_intan_rhd_format_one_amp_channel import read_data as read_intan_one_channel
from .mcs.McsData import RawData as read_mcs
from .spike2.read_data import read_smr as read_spike2
from .multimed.read_data import read_multimed_data as read_multimed
from .mcs import mymcsutil
from .intan import myintanutil
import numpy as np

class datatypes:
    def __init__(self):
        self.NONE     = 0
        self.INTAN    = 1
        self.MCS      = 2
        self.HDF5     = 2 # Same thing as MCS for now but will have to change eventually
        self.SMR      = 3 # SMR support is really bad. Like, really, really bad, use at own peril.
        self.MED      = 4 # Binary files for/from Multimed; Primary naming convention
        self.MULTIMED = 4 # Binary files for/from Multimed; Secondary naming convention just in case I forget
    def recognize(self, file_path):
        if not(file_path):
            warn(colprint.printwar)(f"Warning : did not recognize data type (no file specified)")
            return self.NONE
        # TODO : recognize by header where possible
        i_extension = file_path.rfind(".")
        extension = file_path[i_extension:]
        if extension == ".rhd":
            return self.INTAN
        elif extension == ".mcd":
            colprint.printerr("*.mcd files need to be converted to *.h5 format.")
            return self.NONE
        elif extension == ".h5":
            return self.HDF5
        elif extension == ".smr":
            return self.SMR
        elif extension == ".bin":
            return self.MED
        else:
            colprint.printerr(f"Error : did not recognize data type from file {file_path}")
            return self.NONE

    def name(self, which):
        if which == self.NONE:
            return "NONE"
        if which == self.INTAN:
            return "INTAN"
        if which == self.HDF5:
            return "HDF5"
        if which == self.MCS:
            return "MCS"
        if which == self.SMR:
            return "SMR"
        if which == self.MED:
            return "MULTIMED"

DATATYPES = datatypes()

class DataSource:
    def __init__(self, path):
        self.file_path = path
        self.type = DATATYPES.recognize(path)
        self._checkDatatype()
        self.data = None
        self._set_default_parameters()
    def getFs(self, i=0):
        self._checkDatatype()
        self._checkDataLoaded()
        if self.type == DATATYPES.INTAN:
            Fs = 1. * self.data['frequency_parameters']['board_adc_sample_rate']
            return Fs
        if self.type == DATATYPES.HDF5:
            r = self.import_parameters["recording_idx"]
            a = self.import_parameters["analog_stream_idx"]
            Fs = 1. * self.data.recordings[r].analog_streams[a].channel_infos[i].sampling_frequency.magnitude
            return Fs
        if self.type == DATATYPES.SMR:
            Fs = float(self.data.segments[0].analogsignals[i].sampling_rate.magnitude)
            return Fs
        if self.type == DATATYPES.MED:
            return self.data['Fs']
    def getSignal(self, i, bounds=None, bounds_s=None, bounds_samples=None):
        """ These shenanigans for backwards compatibility : use NONE or ONE of the three : bounds (in samples), bounds_s (in seconds), bounds_samples (in samples)"""
        if not(bounds) and not(bounds_s) and not(bounds_samples):
            bounds = None
        elif bounds and not(bounds_s) and not(bounds_samples):
            bounds = bounds
        elif not(bounds) and bounds_s and not(bounds_samples):
            bounds = (int(bounds_s[0] * self.getFs()), int(bounds_s[1] * self.getFs()))
        elif not(bounds) and not(bounds_s) and bounds_samples:
            bounds = bounds_samples
        else:
            print("Invalid bounds definition in getSignal")
            raise
        """ Back to the meat of the function """
        self._checkDatatype()
        self._checkDataLoaded()
        if self.type == DATATYPES.INTAN:
            if not(self.import_parameters["is_huge"]):
                signal = self.data['amplifier_data'][i]# if not bounds else self.data['amplifier_data'][i]
            else:
                if (self.data["currently_loaded"]["channel"] != i):
                    print("DataManager : huge data request changed, loading new data ...")
                    self.load_one_channel(i)
                signal = self.data['amplifier_data']# if not bounds else self.data['amplifier_data'][bounds[0]:bounds[1]]
        if self.type == DATATYPES.HDF5:
            r = self.import_parameters["recording_idx"]
            a = self.import_parameters["analog_stream_idx"]
            quantum = self.data.recordings[r].analog_streams[a].channel_infos[i].adc_step.to("microvolts").magnitude
            signal_i4 = self.data.recordings[r].analog_streams[a].channel_data[i] if not bounds else self.data.recordings[r].analog_streams[a].channel_data[i,:]
            signal = quantum * signal_i4
        if self.type == DATATYPES.SMR:
            signal = np.concatenate([segment.analogsignals[i].magnitude.flatten() for segment in self.data.segments])
        if self.type == DATATYPES.MED:
            signal = self.data['data'][:, i]# if not bounds else self.data['data'][bounds[0]:bounds[1], i]

        """ Blank & return """
        for blank in self.import_parameters["blank"]:
            i0 = int(blank[0] * self.getFs())
            i1 = int(blank[1] * self.getFs())
            signal[i0:i1] = 0
        return signal if not bounds else signal[bounds[0]:bounds[1]]
    def translateChannel(self, E):
        self._checkDatatype()
        self._checkDataLoaded()
        if self.type == DATATYPES.INTAN:
            e = myintanutil.get_channelIdx(E, self.data)
            return e
        if self.type == DATATYPES.HDF5:
            r = self.import_parameters["recording_idx"]
            a = self.import_parameters["analog_stream_idx"]
            e = mymcsutil.get_channelIdx(E, self.data, r, a)
            return e
        if self.type == DATATYPES.SMR:
            for i,ch in enumerate(self.data.segments[0].analogsignals):
                if ch.name == E:
                    return i
            return None
        if self.type == DATATYPES.MED:
            return int(E)
    def getFrontend(self):
        self._checkDatatype()
        self._checkDataLoaded()
        if self.type == DATATYPES.HDF5 :
            return "MCS" # Can we find the exact information in the file ?
        if self.type == DATATYPES.INTAN :
            return "INTAN" # Can we find the exact information in the file ?
        return "Unknown"
    def getAllChannels(self, custom_or_native=1):
        self._checkDatatype()
        if self.type == DATATYPES.INTAN:
            which = "native_channel_name" if custom_or_native else "custom_channel_name"
            return myintanutil.get_allChannels() # FIXME
        if self.type == DATATYPES.HDF5:
            return mymcsutil.get_allChannels(self.data, recording_index=self.import_parameters["recording_idx"], stream_index=self.import_parameters["analog_stream_idx"]) # FIXME
    def getAvailableChannels(self, custom_or_native=1):
        self._checkDatatype()
        if self.data is None:
            self.load() # force load
        if self.type == DATATYPES.SMR:
            channels = [ch.name for ch in self.data.segments[0].analogsignals]
            print(channels)
            return channels
        elif self.type == DATATYPES.INTAN:
            which = "native_channel_name" if custom_or_native else "custom_channel_name"
            channels = [chan[which] for chan in self.data['amplifier_channels']]
        else:
            channels = []
        return channels

    def load(self):
        self._checkDatatype()
        if self.type == DATATYPES.INTAN:
            if not(self.import_parameters["is_huge"]):
                self.data = read_intan(self.file_path)
            else:
                self.data = read_intan_header(self.file_path)
                self.data["currently_loaded"] = {"channel": None}
        if self.type == DATATYPES.HDF5:
            self.data = read_mcs(self.file_path)
        if self.type == DATATYPES.SMR:
            self.data = read_spike2(self.file_path)
        if self.type == DATATYPES.MED:
            self.data = read_multimed(self.file_path, quantum=self.import_parameters['quantum'])
    def load_one_channel(self, i):
        if self.type == DATATYPES.INTAN:
            self.data = read_intan_one_channel(self.file_path, i)
            self.data["currently_loaded"] = {"channel": i}
        if self.type == DATATYPES.HDF5:
            print("Unsupported")
            self.data = {}
        if self.type == DATATYPES.SMR:
            print("Unsupported")
            self.data = {}

    def unload(self):
        del self.data
        self.data = None
    def _set_default_parameters(self):
        self.import_parameters = {}
        self.import_parameters["blank"] = []
        if self.type == DATATYPES.HDF5:
            self.import_parameters["recording_idx"] = 0
            self.import_parameters["analog_stream_idx"] = 0
        if self.type == DATATYPES.INTAN:
            self.import_parameters["is_huge"] = False
        if self.type == DATATYPES.MED:
            self.import_parameters["quantum"] = 1
    def setImportParameters(self, parameters):
        for k in parameters:
            self.import_parameters[k] = parameters[k]
        # print("DataManager : New import parameters :")
        # print(self.import_parameters)
    def _checkDatatype(self):
        if self.type is DATATYPES.NONE:
            raise Exception("DataSource : Unrecognized type.")
    def _checkDataLoaded(self):
        if not(self.data):
            raise Exception("Datasource : Data not loaded.")
