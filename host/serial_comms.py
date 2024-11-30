from PyQt5 import QtCore
import struct
import crcmod
import time
from data_series import DataPoint

BAUDRATE = 115200
MAGIC = b'PRZL'  # Expected magic bytes
MAGIC_ACK = b'ACK!'

RX_PACKET_SIZE = 4 + 8 * 4 + 4 + 4  # 4 bytes for magic, 8 floats, 4 bytes for valve states + packing, 4 bytes for CRC


def calculate_crc(data):
    pcrc = crcmod.Crc(0x104c11db7, initCrc=0xffffffff, rev=False)
    pcrc.update(data)
    return pcrc.crcValue


# Set channel format:
# '<' indicates little-endian byte order; all fields are packed tightly
rx_valve_cmd_format = '<4s8B I'  # 4 bytes for magic, 8 bytes for state_changes, 4 bytes for crc
rx_valve_cmd_magic = b'VCMD'

# 4 bytes magic, 1 byte valve  channel, 1 byte enabled, 1 byte open_above, 1 byte source channel, 2 float pressure values, 1 uint32 crc
rx_auto_valve_cmd_format = '<4s B B B B f f I'
rx_auto_valve_cmd_magic = b'AUTO'

rx_calibration_magic = b'CALB'

CHANNEL_NOP = 0
CHANNEL_SET = 1
CHANNEL_RESET = 2
CHANNEL_TOGGLE = 3


# Pass a dict of {channel:action}, like {1: CHANNEL_SET, 2:CHANNEL_TOGGLE}
def create_tx_set_packet(actions):
    channel_actions = [CHANNEL_NOP] * 8
    for channel in range(8):
        if channel in actions:
            channel_actions[channel] = actions[channel]

    tx_struct = struct.pack(rx_valve_cmd_format, rx_valve_cmd_magic, *channel_actions, 0)
    tx_struct = struct.pack(rx_valve_cmd_format, rx_valve_cmd_magic, *channel_actions, calculate_crc(tx_struct[:-4]))

    return tx_struct


def create_tx_autoctl_packet(channel, enabled, open_above, source_channel, pressure, pressure_hyst):
    tx_struct = struct.pack(rx_auto_valve_cmd_format, rx_auto_valve_cmd_magic, int(channel), int(enabled), int(open_above), int(source_channel), float(pressure), float(pressure_hyst), 0)
    tx_struct = struct.pack(rx_auto_valve_cmd_format, rx_auto_valve_cmd_magic, int(channel), int(enabled), int(open_above), int(source_channel), float(pressure), float(pressure_hyst), calculate_crc(tx_struct[:-4]))

    return tx_struct


def create_tx_calib_packet():
    return rx_calibration_magic


class SerialWorker(QtCore.QObject):
    new_data_signal = QtCore.pyqtSignal(DataPoint)
    new_valve_signal = QtCore.pyqtSignal(list)
    ack_signal = QtCore.pyqtSignal()

    def __init__(self, ser, data_rx_slot, valve_rx_slot, parent=None):
        super(self.__class__, self).__init__(parent)
        self.ser = ser
        self.data_rx_slot = data_rx_slot
        self.valve_rx_slot = valve_rx_slot
        self.running = True

    @QtCore.pyqtSlot()
    def start_work(self):
        if self.ser is None:
            return

        # connect data signal
        self.new_data_signal.connect(self.data_rx_slot)
        self.new_valve_signal.connect(self.valve_rx_slot)
        raw_data = bytearray(b'')
        raw_data.extend(self.ser.read(4))

        while self.running:
            # print('.', end='')
            # Read the expected packet size from the serial port
            rx_timestamp = time.time()

            # Unpack the packet
            try:
                header = struct.unpack('<4s', raw_data[0:4])[0]
                if header == MAGIC:
                    if len(raw_data) >= RX_PACKET_SIZE:
                        self.handle_data_rx(raw_data, rx_timestamp)
                        raw_data.clear()
                        raw_data.extend(self.ser.read(4))
                        continue
                elif header == MAGIC_ACK:
                    print('ack')
                    self.ack_signal.emit()
                    raw_data.clear()
                    raw_data.extend(self.ser.read(4))
                    continue
                elif len(raw_data) >= 4:
                    raw_data.pop(0)
                    raw_data.extend(self.ser.read(1))
                    print("Magic bytes mismatch. Discarding byte.")
                    continue

                raw_data.extend(self.ser.read(1))
            except struct.error as e:
                print("Failed to unpack data:", e)
        print('stopped rxing')

    def handle_data_rx(self, raw_data, rx_timestamp):
        try:
            unpacked_data = struct.unpack('<4s8fB3sI', raw_data)
            pressures = unpacked_data[1:9]
            valve_state_bits = unpacked_data[9]

            received_crc = unpacked_data[-1]

            # Calculate CRC on the received data except the last 4 bytes (the CRC)
            data_for_crc = raw_data[0:-4]
            calculated_crc = calculate_crc(data_for_crc)

            # Verify CRC
            if calculated_crc != received_crc:
                print(f"CRC mismatch! Expected: {received_crc:#010x}, Calculated: {calculated_crc:#010x}")
                return

            # If everything checks out, send the data back to the main thread
            data_point = DataPoint(timestamp=rx_timestamp, data=pressures)
            self.new_data_signal.emit(data_point)

            # Unpack bits of valve states
            valve_states = [(valve_state_bits & (1 << i) != 0) for i in range(8)]
            self.new_valve_signal.emit(valve_states)
            # print("Received pressures:", pressures)

        except struct.error as e:
            print("Failed to unpack data:", e)

    # @QtCore.pyqtSlot()
    def stop_work(self):
        self.running = False
        print('stopped???')
