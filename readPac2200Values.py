import socket
from ctypes import *
from itertools import chain
import time

HOST = "10.59.7.2"
PORT = 502

class PAC2200(Structure):
    _fields_ = [
            ("VL1_N", c_float),
            ("VL2_N", c_float),
            ("VL3_N", c_float),
            ("VL1_VL2", c_float),
            ("VL2_VL3", c_float),
            ("VL1_VL3", c_float),
            ("C_L1", c_float),
            ("C_L2", c_float),
            ("C_L3", c_float),
    ]

    def __init__(self, *args, **kwargs):
        super(PAC2200, self).__init__()
        self.transactionIdentifier = 0
        self.protocolIdentifier = 0
        self.messageLength = 6

    def connect(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        while True:
            try:
                sock.settimeout(2)
                sock.connect((HOST, PORT))
                print("Connected to the server successfully!")
                break
            except socket.error as exc:
                print(exc)
                print("Retrying after 5 seconds...")
                time.sleep(5)
        return sock

    def prepareModbusData(self, start_register, num_registers, unitId = 1):
        request = bytearray([self.transactionIdentifier >> 8, self.transactionIdentifier & 0xFF,
                         self.protocolIdentifier >> 8, self.protocolIdentifier & 0xFF,
                         self.messageLength >> 8, self.messageLength & 0xFF,
                         unitId,
                         0x03,  # Function code: Read Holding Registers
                         start_register >> 8, start_register & 0xFF,
                         num_registers >> 8, num_registers & 0xFF])
        return request

    def getModbusData(self):
        modbus_sock = self.connect()
        try:
            modbus_sock.send(self.prepareModbusData(1, len(self._fields_) * 2))
            received_data = modbus_sock.recv(1024)

            return ["{:02x}".format(byte) for byte in received_data[9:]]
        except socket.error as exc:
            print(exc)
            raise socket.error("Failed to receive data from the server.")
        finally:
            modbus_sock.close()

    def swap_data(self):
        getData = self.getModbusData()
        getData = [getData[i] + getData[i + 1] for i in range(0, len(getData), 2)]
        getData = [int(x, 16) for x in getData]
        self.swapped_data = list(chain.from_iterable(zip(getData[1::2], getData[0::2])))
        for i, field in enumerate(self._fields_):
            setattr(self, field[0], cast(pointer((c_uint16 * 2)(*self.swapped_data[i * 2:(i * 2) + 2])), POINTER(c_float)).contents.value)

if __name__ == "__main__":
    try:
        pac2200 = PAC2200()
        pac2200.swap_data()
        print("VL1_N:", pac2200.VL1_N)
        print("VL2_N:", pac2200.VL2_N)
        print("VL3_N:", pac2200.VL3_N)
        print("VL1_VL2:", pac2200.VL1_VL2)
        print("VL2_VL3:", pac2200.VL2_VL3)
        print("VL1_VL3:", pac2200.VL1_VL3)
        print("C_L1:", pac2200.C_L1)
        print("C_L2:", pac2200.C_L2)
        print("C_L3:", pac2200.C_L3)
    except socket.error as e:
        print("Error:", e)
