import sys
import threading

import matplotlib

matplotlib.use('Qt5Agg')

import numpy as np
from PyQt5.QtCore import QObject, pyqtSignal
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QFrame, QGridLayout, QPushButton
from matplotlib.lines import Line2D

from PyQt5 import QtCore, QtWidgets

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas, \
    NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
from matplotlib.animation import TimedAnimation

class DataPoint:
    def __init__(self, time, data):
        self.time = time
        self.data = data


class DataSeries:
    def __init__(self, data=None, time=None):
        if time is None:
            time = []
        if data is None:
            data = []
        self.data = data
        self.time = time

    def append_from(self, d2):
        self.data.extend(d2.data)
        self.time.extend(d2.timestamps)
        d2.clear()

    def add_point(self, data_point:DataPoint):
        self.data.append(data_point.data)
        self.time.append(data_point.time)

    def clear(self):
        self.data = []
        self.time = []


class MplCanvas(FigureCanvas, TimedAnimation):
    def __init__(self, width=5, height=4, dpi=100):
        self.data_series = DataSeries()
        self.added_data_series = DataSeries()

        self.fig = Figure(figsize=(width, height), dpi=dpi)

        self.axes = self.fig.add_subplot(111)

        self.axes.set_ylim(-100, 100)

        self.line1 = Line2D([], [], color='blue')
        self.line1_tail = Line2D([], [], color='red', linewidth=2)
        self.line1_head = Line2D([], [], color='red', marker='o', markeredgecolor='r')

        self.axes.add_line(self.line1)
        self.axes.add_line(self.line1_tail)
        self.axes.add_line(self.line1_head)

        TimedAnimation.__init__(self, self.fig, interval=50, blit=True)
        FigureCanvas.__init__(self, self.fig)

    def _init_draw(self):
        lines = [self.line1, self.line1_tail, self.line1_head]
        for line in lines:
            line.set_data([], [])
        return

    def addData(self, value):
        self.addedData.add_point(value)
        return

    # noinspection PyProtectedMember
    def _step(self, *args):
        # Extends the _step() method for the TimedAnimation class.
        try:
            TimedAnimation._step(self, *args)
        except Exception as e:
            self.abc += 1
            print(str(self.abc))
            TimedAnimation._stop(self)
            pass
        return

    def _draw_frame(self, framedata):
        self.line1.set_data(self.data_series.time, self.data_series.data)
        self.line1_tail.set_data(self.added_data_series.time, self.added_data_series.data)
        if(len(self.added_data_series.data)) > 0:
            self.line1_head.set_data(self.added_data_series.time[-1], self.added_data_series.data[-1])
        else:
            self.line1_head.set_data([], [])

        self.data_series.append_from(self.added_data_series)
        self._drawn_artists = [self.line1, self.line1_tail, self.line1_head]

        return


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__()

        self.setGeometry(300, 300, 800, 400)
        self.setWindowTitle("my first window")
        # Create FRAME_A
        self.FRAME_A = QFrame(self)
        self.FRAME_A.setStyleSheet("QWidget { background-color: %s }" % QColor(210,210,235,255).name())
        self.LAYOUT_A = QGridLayout()
        self.FRAME_A.setLayout(self.LAYOUT_A)
        self.setCentralWidget(self.FRAME_A)
        # Place the zoom button
        self.zoomBtn = QPushButton(text = 'zoom')
        self.zoomBtn.setFixedSize(100, 50)
        self.zoomBtn.clicked.connect(self.zoomBtnAction)
        self.LAYOUT_A.addWidget(self.zoomBtn, 0, 0)
        # Place the matplotlib figure
        self.mpl_fig = MplCanvas()
        self.LAYOUT_A.addWidget(self.mpl_fig, 0, 1)
        # Add the callbackfunc to send data
        myDataLoop = threading.Thread(name='myDataLoop', target=dataSendLoop, daemon=True, args=(self.addData_callbackFunc,))
        myDataLoop.start()
        self.show()
        return

    def zoomBtnAction(self):
        print('Zoom!')

    def addData_callbackFunc(self, value):
        # print("Add data: " + str(value))
        self.mpl_canvas.addData(value)
        return


# You need to set up a signal slot mechanism, to
# send data to your GUI in a thread-safe way.
# Believe me, if you don't do this right, things
# go very, very wrong...
class Communicate(QObject):
    data_signal = pyqtSignal(float)

def dataSendLoop(addData_callbackFunc):
    # Setup the signal-slot mechanism.
    mySrc = Communicate()
    mySrc.data_signal.connect(addData_callbackFunc)

    # Simulate some data
    n = np.linspace(0, 499, 500)
    y = 50 + 25*(np.sin(n / 8.3)) + 10*(np.sin(n / 7.5)) - 5*(np.sin(n / 1.5))
    i = 0

    while(True):
        if(i > 499):
            i = 0
        time.sleep(0.1)
        mySrc.data_signal.emit(y[i]) # <- Here you emit a signal!
        i += 1


app = QtWidgets.QApplication(sys.argv)
w = MainWindow()
app.exec_()
