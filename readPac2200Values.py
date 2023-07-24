import socket
from ctypes import *
from itertools import chain
import time
import struct

HOST = "10.59.7.2"
PORT = 502

class PAC2200(Structure):

    def __init__(self, *args, **kwargs):
        super(PAC2200, self).__init__()
        self.transactionIdentifier = 0
        self.protocolIdentifier = 0
        self.messageLength = 6
        self.tempData = []    
        self.pacData = {
                "VL1_N": '',
                "VL2_N": '',
                "VL3_N": '',
                "VL1_VL2": '',
                "VL2_VL3": '',
                "VL1_VL3": '',
                "C_L1": '',
                "C_L2": '',
                "C_L3": '',
                "APP_L1": '',
                "APP_L2": '',
                "APP_L3": '',
                "ACP_L1": '',
                "ACP_L2": '',
                "ACP_L3": '',
                "RP_L1": '',
                "RP_L2": '',
                "RP_L3": '',
                "PF_L1": '',
                "PF_L2": '',
                "PF_L3": '',
                "nanVal_1": '',
                "nanVal_2": '',
                "nanVal_3": '',
                "nanVal_4": '',
                "nanVal_5": '',
                "nanVal_6": '',
                "FREQ": '',
                "AV_VL1_N": '',
                "AV_VLL_L": '',
                "AV_C": '',
                "T_AP_P": '',
                "T_AC_P": '',
                "T_RE_P": '',
                "T_P_F": '',
        }

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
            modbus_sock.send(self.prepareModbusData(1, 70))
            received_data = modbus_sock.recv(1024)
            floatParts = ["{:02x}".format(byte) for byte in received_data[9:]]

            modbus_sock.send(self.prepareModbusData(801, 4))
            AC_ENG_IMP_T1 = modbus_sock.recv(1024)

            return [floatParts, AC_ENG_IMP_T1]
        except socket.error as exc:
            print(exc)
            raise socket.error("Failed to receive data from the server.")
        finally:
            modbus_sock.close()

    def partOfData(self):
        floatParts, AC_ENG_IMP_T1 = self.getModbusData()
        for i in range(0, len(floatParts), 4):
            hex_number = ''.join(floatParts[i:i+4])
            self.tempData.append(struct.unpack('>f', bytes.fromhex(hex_number))[0])
        
        AC_ENG_IMP_T1 = struct.unpack('>d', bytes.fromhex(''.join(["{:02x}".format(byte) for byte in AC_ENG_IMP_T1[9:]])))[0]
        for i, key in enumerate(self.pacData): self.pacData[key] = self.tempData[i]

if __name__ == "__main__":
    try:
        pac2200 = PAC2200()
        pac2200.partOfData()
        print(pac2200.pacData)


    except socket.error as e:
        print("Error:", e)
