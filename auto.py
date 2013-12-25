#!/usr/bin/python
from optparse import OptionParser
import os
import sys
import time

import motor
import adxl345


parser = OptionParser()
parser.add_option("-p", "--p", dest="p", help="")
(options, args) = parser.parse_args()


m = motor.Motor()
accel = adxl345.ADXL345()

m.init()

speed_percent = 0

try:
	while (True):
		axis = accel.getAxes()
		pos = m.set_speed(speed_percent/100.0)
		sys.stdout.write("\r[x:%.3f y:%.3f z:%.3f] [%d%% (%d)]" % (axis['x'], axis['y'], axis['z'], speed_percent, pos))
		sys.stdout.flush()
		time.sleep(0.02)
except: pass
finally:
	m.reset()
