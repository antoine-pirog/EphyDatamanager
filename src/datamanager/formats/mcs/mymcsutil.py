def get_channelIdx(which, data, recording_index=0, stream_index=0):
    idx = None
    analog_channels = data.recordings[recording_index].analog_streams[stream_index]
    for i, c in enumerate(analog_channels.channel_infos.values()):
        if which == c.label:
            idx = i
            label = c.label
            break
    if idx is None:
        return None
    print(f"Channel {which} : got index {idx} (label={label}; rec_idx={recording_index}; strm_idx={stream_index})")
    return idx

def get_allChannels(data, recording_index=0, stream_index=0):
    analog_channels = data.recordings[recording_index].analog_streams[stream_index]
    COI_MCS = []
    for c in analog_channels.channel_infos.values():
        if not(c.label in COI_MCS):
            COI_MCS.append(c.label)
    return COI_MCS

def get_unconnectedChannels():
    print("Warning : this only exists for legacy reasons and will get removed")
    chanlist = []
    chanlist.append('15')
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

def stringify(chanlist):
    return [str(c) for c in chanlist]
