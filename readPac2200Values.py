from pymodbus.client.sync import ModbusTcpClient
from ctypes import *
from itertools import chain

class PAC2200(Structure):
    _fields_ = [
            ("VL1_N", c_float),
            ("VL2_N", c_float),
            ("VL3_N", c_float),
            ("VL1_VL2", c_float),
    ]

    def __init__(self, *args, **kwargs):
        super(PAC2200, self).__init__(*args, **kwargs)
        self.Modbus = ModbusTcpClient('10.59.7.2')
        self.returnedData = []

    def getAllValue(self):
        self.data = self.Modbus.read_holding_registers(1, 8, unit=1)
        self.Modbus.close()
        return self.swapData()

    def swapData(self):
        self.swappedData = list(chain.from_iterable(zip(self.data.registers[1::2], self.data.registers[0::2])))
        for i in range(0, len(self._fields_)):
            setattr(self, self._fields_[i][0], cast(pointer((c_uint16 * 2)(*self.swappedData[(i * 2):(i*2)+2])), POINTER(c_float)).contents.value)
            self.returnedData.append({self._fields_[i][0]: getattr(self, self._fields_[i][0])})
        return self.returnedData
    
_pac2200 = PAC2200()
print(_pac2200.getAllValue())





