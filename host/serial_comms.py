from PyQt5 import QtCore
import struct
import crcmod
import time
from data_series import DataPoint

BAUDRATE = 115200
MAGIC = b'PRZL'  # Expected magic bytes
PACKET_SIZE = 4 + 8 * 4 + 4  # 4 bytes for magic, 8 floats, 4 bytes for CRC


def calculate_crc(data):
    pcrc = crcmod.Crc(0x104c11db7, initCrc=0xffffffff, rev=False)
    pcrc.update(data)
    return pcrc.crcValue


class SerialWorker(QtCore.QObject):
    new_data_signal = QtCore.pyqtSignal(DataPoint)

    def __init__(self, ser, data_rx_slot, parent=None):
        super(self.__class__, self).__init__(parent)
        self.ser = ser
        self.data_rx_slot = data_rx_slot
        self.running = True

    @QtCore.pyqtSlot()
    def start_work(self):
        if self.ser is None:
            return

        # connect data signal
        self.new_data_signal.connect(self.data_rx_slot)

        while self.running:
            # print('.', end='')
            # Read the expected packet size from the serial port
            raw_data = self.ser.read(PACKET_SIZE)

            if len(raw_data) != PACKET_SIZE:
                print("Incomplete packet received")
                continue

            rx_timestamp = time.time()

            # Unpack the packet
            try:
                unpacked_data = struct.unpack('<4s8fI', raw_data)
                magic = unpacked_data[0]
                pressures = unpacked_data[1:9]
                received_crc = unpacked_data[9]

                # Check magic bytes
                if magic != MAGIC:
                    print("Magic bytes mismatch. Discarding packet.")
                    continue

                # Calculate CRC on the received data except the last 4 bytes (the CRC)
                data_for_crc = raw_data[0:-4]
                calculated_crc = calculate_crc(data_for_crc)

                # Verify CRC
                if calculated_crc != received_crc:
                    print(f"CRC mismatch! Expected: {received_crc:#010x}, Calculated: {calculated_crc:#010x}")
                    continue

                # If everything checks out, send the data back to the main thread
                data_point = DataPoint(timestamp=rx_timestamp, data=pressures)
                self.new_data_signal.emit(data_point)
                # print("Received pressures:", pressures)

            except struct.error as e:
                print("Failed to unpack data:", e)
        print('stopped rxing')

    # @QtCore.pyqtSlot()
    def stop_work(self):
        self.running = False
        print('stopped???')
