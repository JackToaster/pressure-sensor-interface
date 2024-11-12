import os
import sys
import random
import time
from PyQt5 import QtWidgets, QtCore
import pyqtgraph as pg
from PyQt5.QtWidgets import QFileDialog
from pyqtgraph.parametertree import ParameterTree

from app_state import AppState
from parameters import create_parameters
from serial_connection import SerialConnectionWidget

from data_series import DataSeries, DataPoint


class Application(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        self.state = AppState(n_channels=8)

        # Set up the layout
        self.setWindowTitle("Pneumatic Interface GUI")

        # Create control panel on the left
        self.control_panel = QtWidgets.QVBoxLayout()
        self.serial_conn_ctl = SerialConnectionWidget(self.state)
        self.start_button = QtWidgets.QPushButton("Start")
        self.stop_button = QtWidgets.QPushButton("Stop")
        self.save_button = QtWidgets.QPushButton("Save Data")

        self.param_list = ParameterTree()
        self.params = create_parameters(self.state)
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
            plot = self.state.graph_panel.addPlot(row=i, col=0, axisItems={'bottom': pg.DateAxisItem()})
            plot.showGrid(x=True, y=True)
            plot.setLabel('left', f"P[{i}]")
            plot.setLabel('bottom', "Time")
            plot.setXRange(0, 10)  # Initial time range of 10 seconds
            plot.setYRange(-10, 10)  # Set reasonable Y-axis range for signal
            plot.setDownsampling(mode='peak')
            plot.showGrid(x=True, y=True)
            plot_curve = plot.plot(pen=pg.mkPen(color=(i * 30, 100, 200)), fillLevel=-0.3, brush=(50, 50, 200, 100))
            self.state.graphs.append(plot)
            self.state.plots.append(plot_curve)

        for i in range(1, 8):
            self.state.graphs[i].setXLink(self.state.graphs[0])

        # Add control and graph panels to main layout
        self.layout = QtWidgets.QSplitter()

        left = QtWidgets.QFrame()
        left.setLayout(self.control_panel)
        self.layout.addWidget(left)

        self.layout.addWidget(self.state.graph_panel)

        self.layout.setStretchFactor(1, 1)
        self.layout.setSizes([125, 150])

        hbox = QtWidgets.QHBoxLayout()
        hbox.addWidget(self.layout)
        self.setLayout(hbox)
        # Connect buttons to methods
        self.start_button.clicked.connect(self.start_data)
        self.stop_button.clicked.connect(self.stop_data)
        self.save_button.clicked.connect(self.save_data)

        # Timer for updating graphs
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update_data)
        self.running = False

    def start_data(self):
        self.running = True
        self.state.data.clear()  # Reset data arrays
        self.timer.start(10)  # Update every 10ms TODO make this serial based

    def stop_data(self):
        self.running = False
        self.timer.stop()

    def save_data(self):
        timestamp = time.strftime("%Y%m%d-%H%M%S")
        filename = f"{os.path.dirname(os.path.realpath(__file__))}/data_{timestamp}.csv"
        filename = QFileDialog.getSaveFileName(self, "Save data", filename, "Comma-separated values (*.csv)")[0]
        if filename == '':
            print('Data not saved')
            return
        self.data.save_to_file(filename)

    def update_data(self):
        if not self.running:
            return

        current_time = time.time()

        new_datapoint = DataPoint(timestamp=current_time, data=[])

        for i in range(self.state.n_channels):
            new_value = random.uniform(-10, 10)  # Generate random data point
            new_datapoint.data.append(new_value)

        self.state.data.add_point(new_datapoint)

        self.update_plots()

    def update_plots(self):
        for i in range(8):
            self.state.plots[i].setData(x=self.state.data.timestamps, y=self.state.data.data[i])


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    main = Application()
    main.show()
    sys.exit(app.exec_())
