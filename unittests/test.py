""" Ensure module tested can be imported """
import sys
sys.path.append("../../") # datamanager is there

""" Module to test """
from datamanager import manager

""" Test files """
testvectors = [
    {
        "path" : "../../testdata/Perf_noise nouveau compresseur_201211_152948.rhd",
        "channel_translation" : [("A-000", 0), ("B-031", 63)], # (channel_name, expected_channel_idx)
    },
    {
        "path" : "../../testdata/20210601_HD4_WT_downsampling.h5",
        "channel_translation" : [("H6", 0), ("H2", 59)], # (channel_name, expected_channel_idx)
    },
    {
        "path" : "../../testdata/20211101_SYAMV1_DAQ_MEA_heaton.bin",
        "channel_translation" : [("0", 0), ("63", 63)], # (channel_name, expected_channel_idx)
    }
]

for vector in testvectors:
    print(f"##############################################################################")
    print(f"#")
    print(f"# TESTING .{vector['path'].rsplit('.')[-1]} FILES")
    print(f"#")
    print(f"##############################################################################")

    """ Load test """
    DS = manager.DataSource(vector["path"])
    DS.load()

    """ Get channels test """
    print(DS.getChannels())

    """ Get signal """
    print(DS.getSignal(0))

    """ Get signal (single channel) """
    DS.unload()
    DS.load_one_channel(0)
    print(DS.getSignal(0))

    """ Channel translation """
    for chname,chidx in vector["channel_translation"]:
        assert DS.translateChannel(chname) == chidx
    