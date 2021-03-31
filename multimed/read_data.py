import os
import numpy as np

def read_multimed_data(path, quantum=1):
    filesize = os.path.getsize(path)
    Nchannels = 64
    Nsamples = int(filesize / (Nchannels * 2))
    with open(path, 'rb') as fid:
        data = np.fromfile(fid, dtype='>i2', count=Nsamples*Nchannels)
    data = data.reshape(Nsamples, Nchannels)
    return {'data': data*quantum, 'Fs': 10000, 'len': Nsamples, 'channels': [i for i in range(64)], 'quantum': quantum}
