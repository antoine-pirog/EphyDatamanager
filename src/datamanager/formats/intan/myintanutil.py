def get_channelIdx(which, data):
    idx = None
    ampchannels = data['amplifier_channels']
    for i, c in enumerate(ampchannels):
        if (which == c['native_channel_name']) or (which == c['custom_channel_name']):
            idx = i
            break
    if idx is None:
        return None
    return idx

def get_allChannels():
    return [c + "-" + format(i, "03") for c in ["A", "B"] for i in range(32)]

def get_unconnectedChannels():
    print("Warning : this only exists for legacy reasons and will get removed; This is only true for SYAM experiments using the crown PCB with unconnected GND (V1)")
    chanlist = []
    chanlist.append("B-000")
    chanlist.append("B-001")
    chanlist.append("B-029")
    chanlist.append("B-030")
    chanlist.append("B-031")
    return chanlist

def rem_unconnectedChannels(chanlist):
    # Mutates the object
    to_remove = get_unconnectedChannels()
    rem_channels(chanlist, to_remove)

def rem_channels(chanlist, chans_to_remove):
    # Mutates the object
    for c in chans_to_remove:
        try:
            chanlist.remove(c)
        except:
            pass

def intan2ies(which):
    pass
