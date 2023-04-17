import numpy as np
import serial

# Byte codes
EXCODE = 0x55
BLINK = 0x16

class TGAM:
    def __init__(self, parser_name=None):
        self.debug = False
        self.connection = None
        self.readedBytes = None
        self.rawDataBytes = 512
        self.eAttention = 0
        self.eMeditation = 0

        self.parse_data = self.parse_data()
        self.state = ""
        self.sending_data = False
        self.raw_data = []
        self.noise_data = []
        self.band_list = []
        next(self.parse_data)

    def connect(self, serialPort, baudRate=57600, bytesize=8, parity='N', stopbits=1, timeout=None, numberOfByte=512):
        try:
            self.connection = serial.Serial(serialPort)
            self.connection.port = serialPort
            self.connection.baudrate = baudRate
            self.connection.bytesize = bytesize
            self.connection.parity = parity
            self.connection.stopbits = stopbits
            self.connection.timeout = timeout
            return True
        except:
            return False

    def read(self, numberOfBytes=512):
        if self.connection is not None:
            self.rawDataBytes = numberOfBytes
            self.readedBytes = self.connection.read(numberOfBytes)
            for c in self.readedBytes:
                self.parse_data.send(c)
            return True
        else:
            return False

    def parse_data(self):
        """
            This generator parses one byte at a time.
        """
        while 1:
            byte = yield
            if byte == 0xaa:
                byte = yield  # This byte should be "\aa" too
                if byte == 0xaa:  # packet synced by 0xaa 0xaa
                    # if self.debug: print("synced")
                    packet_length = yield
                    packet_code = yield
                    if packet_code == 0xc0:  # Connect
                        if self.debug: self.state = "connected"

                    else:
                        left = packet_length - 2
                        while left > 0:
                            if packet_code == 0x80:  # Raw value
                                row_length = yield
                                low_byte = yield
                                high_byte = yield
                                # shift bits and take care of signed values
                                raw_value = (high_byte << 8) | low_byte
                                if raw_value > 32768:
                                    raw_value = raw_value - 65536

                                left -= 2
                                self.raw_data = raw_value

                            elif packet_code == 0x02:  # Poor signal
                                poor_byte = yield
                                if self.debug: print("poor signals: ", poor_byte)
                                self.noise_data.append(poor_byte)

                                if poor_byte == 200:
                                    if self.debug: print("electrode not touching the skin")
                                left -= 1

                            elif packet_code == 0x04:  # Attention (eSense)
                                attn_byte = yield
                                if self.debug: print("attention", attn_byte)
                                if attn_byte <= 100:
                                    self.eAttention = attn_byte
                                left -= 1

                            elif packet_code == 0x05:  # Meditation (eSense)
                                med_byte = yield
                                if self.debug: print("meditation", med_byte)

                                if med_byte <= 100:
                                    self.eMeditation = med_byte

                                left -= 1

                            elif packet_code == 0x16:  # Blink not work
                                blink_byte = yield
                                # print("blink", blink_byte)
                                left -= 1

                            elif packet_code == 0x83:  # Bands
                                vector_length = yield
                                current_vector = []
                                for row in range(8):
                                    band_low_byte = yield
                                    band_middle_byte = yield
                                    band_high_byte = yield
                                    value = (band_high_byte << 16) | (band_middle_byte << 8) | band_low_byte
                                    current_vector.append(value)

                                left -= vector_length

                                bands_array = np.array(current_vector)
                                bands_normalized = bands_array / bands_array.sum()
                                # assign bands
                                band_data = {"delta": bands_normalized[0],
                                             "theta": bands_normalized[1],
                                             "low-alpha": bands_normalized[2],
                                             "high-alpha": bands_normalized[3],
                                             "low-beta": bands_normalized[4],
                                             "high-beta": bands_normalized[5],
                                             "low-gamma": bands_normalized[6],
                                             "mid-gamma": bands_normalized[7]
                                             }
                                self.band_list = band_data

                            packet_code = yield
                else:
                    pass  # sync failed
            else:
                pass  # sync failed
