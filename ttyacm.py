#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys
import os
import serial
import io

dev = "/dev/ttyACM0"

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
	sys.stdout.write("\r%4d:%4d:%4d diff:%d ratio:%f adjust:%f velocity:%f               " % (axis['x'], axis['y'], axis['z'], diff, ratio, adjust, velocity))
	sys.stdout.flush()

s.close()
