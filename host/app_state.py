from data_series import DataSeries
import pyqtgraph as pg

class AppState:
    def __init__(self, n_channels=8):
        self.graphs = []
        self.plots = []
        self.n_channels = n_channels

        self.graph_panel = pg.GraphicsLayoutWidget()

        self.data = DataSeries(n_channels=n_channels)

        self.serial_connection = None
