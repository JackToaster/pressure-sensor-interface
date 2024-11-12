
class DataPoint:
    def __init__(self, timestamp, data):
        self.timestamp = timestamp
        self.data = data


class DataSeries:
    def __init__(self, data=None, timestamps=None, n_channels=1):
        if timestamps is None:
            timestamps = []
        if data is None:
            data = [[] for _ in range(n_channels)]

        self.data = data
        self.timestamps = timestamps
        self.n_channels = n_channels

    def append_from(self, d2):
        if d2.n_channels != self.n_channels:
            raise ValueError('wrong number of data channels!!1!one')

        for i in range(self.n_channels):
            self.data[i].extend(d2.data[i])
        self.timestamps.extend(d2.timestamps)
        d2.clear()

    def add_point(self, data_point: DataPoint):
        for i in range(self.n_channels):
            self.data[i].append(data_point.data[i])
        self.timestamps.append(data_point.timestamp)

    def clear(self):
        self.data = [[] for _ in range(self.n_channels)]
        self.timestamps = []

    def save_to_file(self, filename):
        with open(filename, 'w') as f:
            for i, line in enumerate(zip(*self.data)):
                f.write(f"{self.timestamps[i]}," + ",".join(map(str, line)) + "\n")
        print(f'Saved data to {filename}')
