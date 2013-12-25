#!/usr/bin/python
# -*- coding: utf-8 -*-

from Adafruit_PWM_Servo_Driver import PWM
import time
import sys
import os
import serial
import io

dev = "/dev/ttyACM0"

servoMin = 150  # Min pulse length out of 4096
servoMax = 600  # Max pulse length out of 4096

# Initialize the PWM device
pwm = PWM(0x40, debug=True)
pwm.setPWMFreq(60)                        # Set frequency to 60 Hz

# Initialize serial
s = serial.Serial(dev, 1000000, timeout=1)

s.write(unicode("\r"))
s.flush()
s.readline()

def cmd(s, cmd):
	for c in cmd:
		s.write(c)
	s.write("\r")
	s.flush()

def get_accelero(s):
	cmd(s, "adxl get_values")
	s.readline()
	s.readline()
	lines = []
	for i in range(3):
		lines.append( s.readline().strip() )
	s.readline()

	axis = {}
	for line in lines:
		parts = line.split("=")
		axis[parts[0].split(" ")[3].lower()] = int(parts[1].strip())

	return axis

target = 0
velocity = 0.0
velocity_max = 100.0
diff_min = -400.0
diff_max = 400.0
while(1):
	axis = get_accelero(s)
	v = axis['x']
	diff = float(target - v)
	adjust = 0
	ratio = 0
	if abs(diff) > 10:
		ratio = (diff / velocity_max) * 0.2
		#print velocity_max, diff
		adjust = abs(diff) * ratio
	velocity += adjust
	if velocity > velocity_max: velocity = velocity_max
	if velocity < 0: velocity = 0
	#print axis

	servoPos = axis['x'] + 400 + servoMin
	if servoPos < servoMin: servoPos = servoMin
	if servoPos > servoMax: servoPos = servoMax
	pwm.setPWM(0, 0, servoPos)

	# Output
	sys.stdout.write("\r%4d:%4d:%4d diff:%d ratio:%f adjust:%f velocity:%f               " % (axis['x'], axis['y'], axis['z'], diff, ratio, adjust, velocity))
	sys.stdout.flush()

s.close()

