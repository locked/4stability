from Adafruit_PWM_Servo_Driver import PWM
import time
import sys

class Motor():
	servoMin = 150  # Min pulse length out of 4096
	servoMax = 600  # Max pulse length out of 4096
	servoInit = 185
	servoMotorStart = 220

	pwm = None

	def __init__(self, debug=True):
		# Initialise the PWM device using the default address
		self.pwm = PWM(0x40, debug=debug)
		self.pwm.setPWMFreq(60)           # Set frequency to 60 Hz
		self.reset()

	def init(self):
		print "Init...",
		self.pwm.setPWM(0, 0, self.servoInit)
		time.sleep(3)
		print "Done"

	def reset(self):
		print "Reset servo (minimum) %d" % self.servoMin
		self.pwm.setPWM(0, 0, self.servoMin)

	def set_speed(self, percent):
		if percent > 1 or percent < 0:
			print "Invalid value, must be between 0 and 1"
		servo_pos = int((self.servoMax - self.servoMotorStart) * percent + self.servoMotorStart)
		#print "Set to %.2f%% (%d)" % (percent, servo_pos)
		self.pwm.setPWM(0, 0, servo_pos)
		return servo_pos

