import smbus
import math

class MPU6050:
	bus = None

	power_mgmt_1 = 0x6b
	power_mgmt_2 = 0x6c

	address = 0x68


	def read_byte(self, adr):
	    return self.bus.read_byte_data(self.address, adr)

	def read_word(self, adr):
	    high = self.bus.read_byte_data(self.address, adr)
	    low = self.bus.read_byte_data(self.address, adr+1)
	    val = (high << 8) + low
	    return val

	def read_word_2c(self, adr):
	    val = self.read_word(adr)
	    if (val >= 0x8000):
	        return -((65535 - val) + 1)
	    else:
	        return val

	def dist(self, a, b):
	    return math.sqrt((a*a)+(b*b))

	def get_y_rotation(self, x, y, z):
	    radians = math.atan2(x, self.dist(y,z))
	    return -math.degrees(radians)

	def get_x_rotation(self, x, y, z):
	    radians = math.atan2(y, self.dist(x,z))
	    return math.degrees(radians)


	def init(self):
		self.bus = smbus.SMBus(1)
		# Wake up the 6050
		self.bus.write_byte_data(self.address, self.power_mgmt_1, 0)


	def readall(self):
		gyro_x = self.read_word_2c(0x43)
		gyro_y = self.read_word_2c(0x45)
		gyro_z = self.read_word_2c(0x47)
		gyro_x_scaled = gyro_x / 131.0
		gyro_y_scaled = gyro_y / 131.0
		gyro_z_scaled = gyro_z / 131.0

		accel_x = self.read_word_2c(0x3b)
		accel_y = self.read_word_2c(0x3d)
		accel_z = self.read_word_2c(0x3f)
		accel_x_scaled = accel_x / 16384.0
		accel_y_scaled = accel_y / 16384.0
		accel_z_scaled = accel_z / 16384.0

		rot_x = self.get_x_rotation(accel_x_scaled, accel_y_scaled, accel_z_scaled)
		rot_y = self.get_y_rotation(accel_x_scaled, accel_y_scaled, accel_z_scaled)

		data = {
			'gyro': {'x': gyro_x, 'y': gyro_y, 'z': gyro_z},
			'gyro_scaled': {'x': gyro_x_scaled, 'y': gyro_y_scaled, 'z': gyro_z_scaled},
			'accel': {'x': accel_x, 'y': accel_y, 'z': accel_z},
			'accel_scaled': {'x': accel_x_scaled, 'y': accel_y_scaled, 'z': accel_z_scaled},
			'rotation': {'x': rot_x, 'y': rot_y}
		}

		return data

