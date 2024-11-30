import sys
from PyQt5 import QtWidgets, QtCore, QtGui

import serial
import serial.tools.list_ports

# from monitor_GUI import Application


class SerialConnectionWidget(QtWidgets.QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent

        # Initialize layout and components
        self.setLayout(QtWidgets.QVBoxLayout())

        # TODO Connection status text
        self.label = QtWidgets.QLabel()
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        font = QtGui.QFont()
        font.setPointSize(16)
        self.label.setFont(font)
        self.label.setStyleSheet("color: red;")
        self.label.setText("Not connected")

        self.layout().addWidget(self.label)

        control_hbox = QtWidgets.QHBoxLayout()
        control_frame = QtWidgets.QFrame()
        control_frame.setLayout(control_hbox)

        self.layout().addWidget(control_frame)

        # Create dropdown for serial devices
        self.port_dropdown = QtWidgets.QComboBox()
        control_hbox.addWidget(self.port_dropdown)

        # Create refresh button
        self.refresh_button = QtWidgets.QPushButton("Refresh")
        control_hbox.addWidget(self.refresh_button)

        # Create connect/disconnect button
        self.connect_button = QtWidgets.QPushButton("Connect")
        control_hbox.addWidget(self.connect_button)

        # Initial state
        self.parent.serial_connection = None
        self.refresh_ports()

        # Connect signals to actions
        self.refresh_button.clicked.connect(self.refresh_ports)
        self.connect_button.clicked.connect(self.toggle_connection)

    def _not_connected(self):
        self.label.setStyleSheet("color: red;")
        self.label.setText("Not connected")

    def _connected(self):
        self.label.setStyleSheet("color: green;")
        self.label.setText("Connected")

    def refresh_ports(self):
        """ Refresh the list of available serial ports. """
        self.port_dropdown.clear()
        ports = serial.tools.list_ports.comports()
        for port in ports:
            self.port_dropdown.addItem(port.device)

    def toggle_connection(self):
        """ Connect or disconnect to the selected serial device. """
        if self.parent.serial_connection is None:
            # Connect
            port_name = self.port_dropdown.currentText()
            if port_name:
                try:
                    self.parent.serial_connection = serial.Serial(port_name, baudrate=115200, timeout=1, write_timeout=1)
                    self.connect_button.setText("Disconnect")
                    print(f"Connected to {port_name}")

                    # Update label
                    self._connected()
                except serial.SerialException as e:
                    QtWidgets.QMessageBox.critical(self, "Connection Error", str(e))
                    self._not_connected()

        else:
            # Disconnect
            self.parent.serial_connection.close()
            self.parent.serial_connection = None
            self.connect_button.setText("Connect")
            print("Disconnected")
            self._not_connected()
