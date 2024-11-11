import struct
import serial
import crcmod

# Constants
SERIAL_PORT = "/dev/ttyACM2"  # Replace with your serial port
BAUDRATE = 115200
MAGIC = b'PRZL'  # Expected magic bytes
PACKET_SIZE = 4 + 8 * 4 + 4  # 4 bytes for magic, 8 floats, 4 bytes for CRC

# CRC calculation function using STM32 polynomial
stm32_crc32 = crcmod.mkCrcFun(0x104C11DB7, initCrc=0xFFFFFFFF, rev=False)


def calculate_crc(data):
    return stm32_crc32(data)


# Main function to read and parse data
def read_serial_data():
    with serial.Serial(SERIAL_PORT, BAUDRATE, timeout=1) as ser:
        while True:
            # Read the expected packet size from the serial port
            raw_data = ser.read(PACKET_SIZE)

            if len(raw_data) != PACKET_SIZE:
                print("Incomplete packet received")
                continue

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
                data_for_crc = raw_data[4:-4]
                calculated_crc = calculate_crc(data_for_crc)

                # Verify CRC
                if calculated_crc != received_crc:
                    print(f"CRC mismatch! Expected: {received_crc:#010x}, Calculated: {calculated_crc:#010x}")
                    continue

                # If everything checks out, print the pressures
                print("Received pressures:", pressures)

            except struct.error as e:
                print("Failed to unpack data:", e)


# Run the function
if __name__ == "__main__":
    read_serial_data()
