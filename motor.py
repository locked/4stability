from Adafruit_PWM_Servo_Driver import PWM
import time
import sys

class Motor():
	servoMin = 150  # Min pulse length out of 4096
	servoMax = 600  # Max pulse length out of 4096
	servoInit = 185
	servoMotorStart = 220

	speed_percent = 0
	asked_speed_percent = 0
	position = 0

	pwm = None
	channel = None
	debug = False

	def __init__(self, channel, debug=True):
		self.channel = channel
		self.debug = debug
		# Initialise the PWM device using the default address
		self.pwm = PWM(0x40, debug=debug)
		self.pwm.setPWMFreq(60)           # Set frequency to 60 Hz
		self.reset()

	def init(self):
		if self.debug: print "Init...",
		self.pwm.setPWM(self.channel, 0, self.servoInit)
		time.sleep(3)
		if self.debug: print "Done"
		return self

	def reset(self):
		if self.debug: print "Reset servo (minimum) %d" % self.servoMin
		self.pwm.setPWM(self.channel, 0, self.servoMin)

	def set_speed(self, percent, min=0, max=1):
		self.asked_speed_percent = percent
		if percent > 1 or percent < 0:
			if self.debug: print "Invalid value, must be between 0 and 1"
		if percent > max:
			percent = max
		if percent < min:
			percent = min
		servo_pos = int((self.servoMax - self.servoMotorStart) * percent + self.servoMotorStart)
		#print "Set to %.2f%% (%d)" % (percent, servo_pos)
		self.pwm.setPWM(self.channel, 0, servo_pos)
		self.position = servo_pos
		self.speed_percent = percent
		return servo_pos

	def adjust_speed(self, diff_speed):
		self.speed_percent = self.speed_percent + diff_speed
		self.set_speed(self.speed_percent/100.0, 0.1, 0.10)

