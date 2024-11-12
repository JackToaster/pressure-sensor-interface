import sys
import random
import time
from PyQt5 import QtWidgets, QtCore
import pyqtgraph as pg
import numpy as np

import serial
import serial.tools.list_ports


class GraphWindow(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        # Set up the layout
        self.setWindowTitle("Real-Time Data Visualization")
        self.layout = QtWidgets.QHBoxLayout(self)

        # Create control panel on the left
        self.control_panel = QtWidgets.QVBoxLayout()
        self.start_button = QtWidgets.QPushButton("Start")
        self.stop_button = QtWidgets.QPushButton("Stop")
        self.save_button = QtWidgets.QPushButton("Save Data")

        # Add buttons to control panel
        self.control_panel.addWidget(self.start_button)
        self.control_panel.addWidget(self.stop_button)
        self.control_panel.addWidget(self.save_button)
        self.control_panel.addStretch()

        # Create graph panel on the right
        self.graph_panel = pg.GraphicsLayoutWidget()
        self.graphs = []
        self.plots = []
        self.data = [[] for _ in range(8)]
        self.timestamps = []

        # Create 8 line graphs in the graph panel
        for i in range(8):
            plot = self.graph_panel.addPlot(row=i, col=0, axisItems={'bottom': pg.DateAxisItem()})
            plot.showGrid(x=True, y=True)
            plot.setLabel('left', f"Signal {i + 1}")
            plot.setLabel('bottom', "Time")
            plot.setXRange(0, 10)  # Initial time range of 10 seconds
            plot.setYRange(-10, 10)  # Set reasonable Y-axis range for signal
            plot.setDownsampling(mode='peak')
            plot.showGrid(x=True, y=True)
            plot_curve = plot.plot(pen=pg.mkPen(color=(i * 30, 100, 200)), fillLevel=-0.3, brush=(50, 50, 200, 100))
            self.graphs.append(plot)
            self.plots.append(plot_curve)

        for i in range(1,8):
            self.graphs[i].setXLink(self.graphs[0])

        # Add control and graph panels to main layout
        self.layout.addLayout(self.control_panel)
        self.layout.addWidget(self.graph_panel)

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
        self.timestamps = []  # Reset timestamps
        self.data = [[] for _ in range(8)]  # Reset data arrays
        self.timer.start(10)  # Update every second

    def stop_data(self):
        self.running = False
        self.timer.stop()

    def save_data(self):
        timestamp = time.strftime("%Y%m%d-%H%M%S")
        filename = f"data_{timestamp}.txt"
        with open(filename, 'w') as f:
            for i, line in enumerate(zip(*self.data)):
                f.write(f"{self.timestamps[i]}\t" + "\t".join(map(str, line)) + "\n")
        print(f"Data saved to {filename}")

    def update_data(self):
        if not self.running:
            return

        current_time = time.time()
        self.timestamps.append(current_time)

        for i in range(8):
            new_value = random.uniform(-10, 10)  # Generate random data point
            self.data[i].append(new_value)
            self.plots[i].setData(x=self.timestamps, y=self.data[i])


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    main = GraphWindow()
    main.show()
    sys.exit(app.exec_())