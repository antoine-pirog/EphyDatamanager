import os
import struct
import numpy as np

def read_multimed_data(path, quantum=1, Fs=10000, Nchannels=64, data_format=">i2"):
    filesize = os.path.getsize(path)
    bytes_per_sample = np.dtype(data_format).itemsize
    Nsamples = int(filesize / (Nchannels * bytes_per_sample))
    # TODO : check that filesize is divisible by Nchannels * bytes_per_sample, otherwise raise a warning
    with open(path, 'rb') as fid:
        data = np.fromfile(fid, dtype=data_format, count=Nsamples*Nchannels)
    data = data.reshape(Nsamples, Nchannels)
    return {'data': data*quantum, 'Fs': Fs, 'len': Nsamples, 'channels': [i for i in range(Nchannels)], 'quantum': quantum}

###############

def read_bin_multichannel(filepath, quantum=1, skip_s=0, length_s=0, Fs=10_000, N_channels=64, data_format=">i2", verbosity=0):
    # filepath : path to the .bin file
    # quantum  : acquisition quantum
    # skip_s   : Time (in seconds) to skip (ie. ignore) at the beginning of the file
    # length_s : Time (in seconds) of data to read (leave 0 to read whole file)
    
    filesize = os.path.getsize(filepath)
    data_width_bytes = np.dtype(data_format).itemsize
    N_samples = int(filesize / (N_channels * data_width_bytes))
    
    # At every sampling time (1/Fs), 64 samples (1 for every channel) are recorded
    # They are recorded in a 128B chunk (2B per channel)
    #   @0x0000 <Sample0/Ch0><Sample0/Ch1><Sample0/Ch2> ... <Sample0/Ch63> (@t=0 s)
    #   @0x0080 <Sample1/Ch0><Sample1/Ch1><Sample1/Ch2> ... <Sample1/Ch63> (@t=0.1 ms)
    #   @0x0100 <Sample2/Ch0><Sample2/Ch1><Sample2/Ch2> ... <Sample2/Ch63> (@t=0.2 ms)
    #                                                   ...
    #   @0x---- <SampleN/Ch0><SampleN/Ch1><SampleN/Ch2> ... <SampleN/Ch63> (@t=N*0.1e-3 s)

    ''' Number of chunks in requested data '''
    skip_chunks   = int(skip_s   * Fs) # Number of chunks to skip
    length_chunks = int(length_s * Fs) # Number of chunks to read
    
    ''' Handle cases where skip_s is unspecified(0) and/or length_s is unspecified (0) '''
    if (length_chunks == 0) and (skip_chunks == 0):
        # If no length or skip specified, read the whole file
        length_chunks = int(filesize / (N_channels * data_width_bytes))
        length_s = length_chunks / Fs
        
    if (length_chunks == 0) and (skip_chunks > 0):
        # If no length specified but non-zero skip, read until end of file
        length_chunks = int(filesize / (N_channels * data_width_bytes) - skip_chunks)
        length_s = length_chunks / Fs
    
    ''' Number of bytes in requested data '''
    skip_bytes   = int(skip_chunks   * N_channels * data_width_bytes)
    length_bytes = int(length_chunks * N_channels * data_width_bytes)
    
    if verbosity >= 1:
        print(f"Reading {length_bytes}B from offset {skip_bytes} (0x{skip_bytes:X})")
    
    ''' Read file'''
    with open(filepath, 'rb') as fid:
        if skip_bytes > 0:
            fid.seek(skip_bytes)
        data = np.fromfile(fid, dtype=data_format, count=length_bytes // data_width_bytes)
    if verbosity >= 2:
        print("20 first points of data (binary values) : ")
        for x in data[:20]:
            print(x, end=',')
        print()
    
    data = data.reshape(length_chunks, N_channels)
    time = np.linspace(skip_s, skip_s+length_s, len(data), endpoint=False)
    
    if verbosity >= 1:
        print("All done.")
    
    return {'data': data*quantum, 'time': time, 'Fs': Fs, 'len': N_samples, 'channels': [i for i in range(N_channels)], 'quantum': quantum}

def read_bin_singlechannel(filepath, ch, quantum=1, skip_s=0, length_s=0, Fs=10_000, N_channels=64, data_format=">i2", verbosity=0):
    # filepath : path to the .bin file
    # quantum  : acquisition quantum
    # skip_s   : Time (in seconds) to skip (ie. ignore) at the beginning of the file
    # length_s : Time (in seconds) of data to read (leave 0 to read whole file)
    
    filesize = os.path.getsize(filepath)
    data_width_bytes = np.dtype(data_format).itemsize
    N_samples = int(filesize / (N_channels * data_width_bytes))
    
    # At every sampling time (1/Fs), 64 samples (1 for every channel) are recorded
    # They are recorded in a 128B chunk (2B per channel)
    #   @0x0000 <Sample0/Ch0><Sample0/Ch1><Sample0/Ch2> ... <Sample0/Ch63> (@t=0 s)
    #   @0x0080 <Sample1/Ch0><Sample1/Ch1><Sample1/Ch2> ... <Sample1/Ch63> (@t=0.1 ms)
    #   @0x0100 <Sample2/Ch0><Sample2/Ch1><Sample2/Ch2> ... <Sample2/Ch63> (@t=0.2 ms)
    #                                                   ...
    #   @0x---- <SampleN/Ch0><SampleN/Ch1><SampleN/Ch2> ... <SampleN/Ch63> (@t=N*0.1e-3 s)

    ''' Number of chunks in requested data '''
    skip_chunks   = int(skip_s   * Fs) # Number of chunks to skip
    length_chunks = int(length_s * Fs) # Number of chunks to read
    
    ''' Handle cases where skip_s is unspecified(0) and/or length_s is unspecified (0) '''
    if (length_chunks == 0) and (skip_chunks == 0):
        # If no length or skip specified, read the whole file
        length_chunks = int(filesize / (N_channels * data_width_bytes))
        length_s = length_chunks / Fs
        
    if (length_chunks == 0) and (skip_chunks > 0):
        # If no length specified but non-zero skip, read until end of file
        length_chunks = int(filesize / (N_channels * data_width_bytes) - skip_chunks)
        length_s = length_chunks / Fs
    
    ''' Number of bytes in requested data '''
    skip_bytes   = int(skip_chunks   * N_channels * data_width_bytes)
    length_bytes = int(length_chunks * N_channels * data_width_bytes)
    
    if verbosity >= 1:
        print(f"Reading {length_bytes}B from offset {skip_bytes} (0x{skip_bytes:X})")
    
    ''' Preallocate data '''
    data = np.zeros((length_chunks,1), dtype=data_format) # Because 1 sample per chunk will be retrieved
    time = np.linspace(skip_s, skip_s+length_s, len(data), endpoint=False)
    
    ''' Read file'''
    with open(filepath, 'rb') as fid:
        SEEK_RELATIVE = 1
        if ch > 0:
            fid.seek(ch * data_width_bytes, SEEK_RELATIVE)
        if skip_bytes > 0:
            fid.seek(skip_bytes, SEEK_RELATIVE)
        for i in range(length_chunks):
            sample, = struct.unpack(data_format, fid.read(data_width_bytes)) # Data format used to be >h, should be equivalent to >i2 or >i16
            data[i] = sample
            fid.seek((N_channels - 1) * data_width_bytes, SEEK_RELATIVE)
    if verbosity >= 2:
        print("20 first points of data (binary values) : ")
        for x in data[:20]:
            print(x, end=',')
        print()
    
    if verbosity >= 1:
        print("All done.")
    
    return {'data': data*quantum, 'time': time, 'Fs': Fs, 'len': N_samples, 'channels': [i for i in range(N_channels)], 'quantum': quantum}