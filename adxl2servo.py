# license: BSD, see LICENSE included in this package
#
# based on awesome lib from Jonathan Williamson (https://github.com/pimoroni/adxl345-python/)
#

from Adafruit_PWM_Servo_Driver import PWM
import smbus
import time
import sys

bus = smbus.SMBus(1)

servoMin = 150  # Min pulse length out of 4096
servoMax = 600  # Max pulse length out of 4096

# Initialize the PWM device
pwm = PWM(0x40, debug=True)
pwm.setPWMFreq(60)                        # Set frequency to 60 Hz

SCALE_MULTIPLIER    = 0.004

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

class ADXL345:
    address = None

    def __init__(self, address = 0x53):        
        self.address = address
        self.setBandwidthRate(BW_RATE_100HZ)
        self.setRange(RANGE_2G)
        self.enableMeasurement()

    def enableMeasurement(self):
        bus.write_byte_data(self.address, POWER_CTL, MEASURE)

    def setBandwidthRate(self, rate_flag):
        bus.write_byte_data(self.address, BW_RATE, rate_flag)

    def setRange(self, range_flag):
        value = bus.read_byte_data(self.address, DATA_FORMAT)
        value &= ~0x0F;
        value |= range_flag;  
        value |= 0x08;
        bus.write_byte_data(self.address, DATA_FORMAT, value)
    
    def getAxes(self):
        bytes = bus.read_i2c_block_data(self.address, AXES_DATA, 6)
        
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

if __name__ == "__main__":
    adxl345 = ADXL345()
    
    while(True):
        axis = adxl345.getAxes()

	servoPos = axis['x'] + 400 + servoMin
	if servoPos < servoMin: servoPos = servoMin
	if servoPos > servoMax: servoPos = servoMax
	pwm.setPWM(0, 0, int(servoPos))

        #print "x:%.3f y:%.3f z:%.3f" % ( axes['x'], axes['y'], axes['z'] )
        sys.stdout.write("\rx:%.3f y:%.3f z:%.3f servoPos:%.3f" % (axis['x'], axis['y'], axis['z'], servoPos))
	sys.stdout.flush()
        time.sleep(0.02)

