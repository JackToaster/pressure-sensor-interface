import os
import sys
import random
import time
from PyQt5 import QtWidgets, QtCore
import pyqtgraph as pg
from PyQt5.QtWidgets import QFileDialog
from pyqtgraph.parametertree import ParameterTree
from pyqtgraph.parametertree.parameterTypes import SimpleParameter

from parameters import create_parameters
from serial_comms import SerialWorker
from serial_connection import SerialConnectionWidget

from data_series import DataSeries, DataPoint

N_CHANNELS = 8


class Application(QtWidgets.QWidget):
    # Signal to start the serial listening worker in a separate thread
    start_serial_sig = QtCore.pyqtSignal()

    def __init__(self):
        super().__init__()

        self.graphs = []
        self.plots = []
        self.n_channels = N_CHANNELS

        self.graph_panel = pg.GraphicsLayoutWidget()

        self.data = DataSeries(n_channels=N_CHANNELS)

        self.serial_connection = None

        self.serial_worker = None
        self.serial_worker_thread = QtCore.QThread(self)

        # Timer for updating graphs
        self.update_graph_timer = QtCore.QTimer()
        self.update_graph_timer.timeout.connect(self.update_plots)
        self.update_graph_timer.setSingleShot(True)
        self.running = False
        self.new_data_available = False

        # Set up the layout
        self.setWindowTitle("Pneumatic Interface GUI")

        # Create control panel on the left
        self.control_panel = QtWidgets.QVBoxLayout()
        self.serial_conn_ctl = SerialConnectionWidget(self)
        self.start_button = QtWidgets.QPushButton("Start")
        self.stop_button = QtWidgets.QPushButton("Stop")
        self.save_button = QtWidgets.QPushButton("Save Data")

        self.param_list = ParameterTree()
        self.params = create_parameters(self)
        self.param_list.setParameters(self.params, showTop=False)

        # Add buttons to control panel
        self.control_panel.addWidget(self.serial_conn_ctl)

        start_stop = QtWidgets.QHBoxLayout()
        start_stop.addWidget(self.start_button)
        start_stop.addWidget(self.stop_button)

        start_stop_frame = QtWidgets.QFrame()
        start_stop_frame.setLayout(start_stop)

        self.control_panel.addWidget(start_stop_frame)
        self.control_panel.addWidget(self.save_button)
        self.control_panel.addSpacing(50)
        self.control_panel.addWidget(self.param_list)
        # self.control_panel.addStretch()

        # Create 8 line graphs in the graph panel TODO Move this to app_state
        for i in range(8):
            plot = self.graph_panel.addPlot(row=i, col=0, axisItems={'bottom': pg.DateAxisItem()})
            plot.showGrid(x=True, y=True)
            plot.setLabel('left', f"P[{i}]")
            plot.setLabel('bottom', "Time")
            plot.setXRange(0, 10)  # Initial time range of 10 seconds
            plot.setYRange(-10, 10)  # Set reasonable Y-axis range for signal
            plot.setDownsampling(mode='peak')
            plot.showGrid(x=True, y=True)
            plot_curve = plot.plot(pen=pg.mkPen(color=(i * 30, 100, 200)), fillLevel=-0.3, brush=(50, 50, 200, 100))
            self.graphs.append(plot)
            self.plots.append(plot_curve)

        for i in range(1, 8):
            self.graphs[i].setXLink(self.graphs[0])

        # Add control and graph panels to main layout
        self.layout = QtWidgets.QSplitter()

        left = QtWidgets.QFrame()
        left.setLayout(self.control_panel)
        self.layout.addWidget(left)

        self.layout.addWidget(self.graph_panel)

        self.layout.setStretchFactor(1, 1)
        self.layout.setSizes([125, 150])

        hbox = QtWidgets.QHBoxLayout()
        hbox.addWidget(self.layout)
        self.setLayout(hbox)
        # Connect buttons to methods
        self.start_button.clicked.connect(self.start_data)
        self.stop_button.clicked.connect(self.stop_data)
        self.save_button.clicked.connect(self.save_data)

    def set_graph_update_time(self, interval_sec: SimpleParameter):
        # Set timer interval in ms
        self.update_graph_timer.setInterval(int(interval_sec.value() * 1000))
        print(f'update rate set to {interval_sec.value()} sec')

    def start_data(self):
        self.running = True
        self.data.clear()  # Reset data arrays
        self.start_serial_worker()
        self.update_graph_timer.start()

    def stop_data(self):
        self.running = False
        self.update_graph_timer.stop()
        self.stop_serial_worker()

    def save_data(self):
        timestamp = time.strftime("%Y%m%d-%H%M%S")
        filename = f"{os.path.dirname(os.path.realpath(__file__))}/data_{timestamp}.csv"
        filename = QFileDialog.getSaveFileName(self, "Save data", filename, "Comma-separated values (*.csv)")[0]
        if filename == '':
            print('Data not saved')
            return
        self.data.save_to_file(filename)

    @QtCore.pyqtSlot(DataPoint)
    def new_data_received(self, datum):
        # print('*', end='')
        self.data.add_point(datum)
        # self.update_plots()
        self.new_data_available = True

    def start_serial_worker(self):
        self.serial_worker = SerialWorker(self.serial_connection, self.new_data_received)
        self.serial_worker.moveToThread(self.serial_worker_thread)
        self.serial_worker_thread.start()

        # Start receiving data
        self.start_serial_sig.connect(self.serial_worker.start_work)
        self.start_serial_sig.emit()

    def stop_serial_worker(self):
        if self.serial_worker is None:
            print('serial worker isn\'t started yet dummy')
            return
        self.serial_worker.stop_work()
        print('stopping serial worker')

        if self.serial_worker is not None:
            self.serial_worker.deleteLater()
            self.serial_worker = None

        self.serial_worker_thread.exit()

    def update_plots(self):
        if self.new_data_available:
            for i in range(8):
                self.plots[i].setData(x=self.data.timestamps, y=self.data.data[i])

        self.new_data_available = False
        if self.running:
            self.update_graph_timer.start()


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    main = Application()
    main.show()
    sys.exit(app.exec_())
