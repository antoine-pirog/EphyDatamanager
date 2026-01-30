from neo import io

def read_smr(file_path):
    reader = io.Spike2IO(filename=file_path)
    data = reader.read(lazy=False, load_waveforms=True)
    return data[0]

if __name__ == "__main__":
    data = read_smr("./test_signal.smr")
