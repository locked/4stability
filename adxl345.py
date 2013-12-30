# license: BSD, see LICENSE included in this package
#
# based on awesome lib from Jonathan Williamson (https://github.com/pimoroni/adxl345-python/)
#

import smbus
import time
import sys

class ADXL345:
    #SCALE_MULTIPLIER    = 0.004
    DATA_FORMAT         = 0x31
    BW_RATE             = 0x2C
    POWER_CTL           = 0x2D

    BW_RATE_1600HZ      = 0x0F
    BW_RATE_800HZ       = 0x0E
    BW_RATE_400HZ       = 0x0D
    BW_RATE_200HZ       = 0x0C
    BW_RATE_100HZ       = 0x0B
    BW_RATE_50HZ        = 0x0A
    BW_RATE_25HZ        = 0x09

    RANGE_2G            = 0x00
    RANGE_4G            = 0x01
    RANGE_8G            = 0x02
    RANGE_16G           = 0x03

    MEASURE             = 0x08
    AXES_DATA           = 0x32

    address = None
    bus = None

    def __init__(self, address=0x53, bwrate=None, range=None):
        self.address = address
        self.bus = smbus.SMBus(1)
        if bwrate is None:
            bwrate = self.BW_RATE_100HZ
        self.setBandwidthRate(bwrate)
        if range is None:
            range = self.RANGE_2G
        self.setRange(range)
        self.enableMeasurement()

    def enableMeasurement(self):
        self.bus.write_byte_data(self.address, self.POWER_CTL, self.MEASURE)

    def setBandwidthRate(self, rate_flag):
        self.bus.write_byte_data(self.address, self.BW_RATE, rate_flag)

    def setRange(self, range_flag):
        value = self.bus.read_byte_data(self.address, self.DATA_FORMAT)
        value &= ~0x0F;
        value |= range_flag;  
        value |= 0x08;
        self.bus.write_byte_data(self.address, self.DATA_FORMAT, value)
    
    def getAxes(self):
        bytes = self.bus.read_i2c_block_data(self.address, self.AXES_DATA, 6)
        
        x = bytes[0] | (bytes[1] << 8)
        if(x & (1 << 16 - 1)):
            x = x - (1<<16)

        y = bytes[2] | (bytes[3] << 8)
        if(y & (1 << 16 - 1)):
            y = y - (1<<16)

        z = bytes[4] | (bytes[5] << 8)
        if(z & (1 << 16 - 1)):
            z = z - (1<<16)

        #x = x * SCALE_MULTIPLIER 
        #y = y * SCALE_MULTIPLIER
        #z = z * SCALE_MULTIPLIER

        x = round(x, 4)
        y = round(y, 4)
        z = round(z, 4)

        return {"x": x, "y": y, "z": z}

