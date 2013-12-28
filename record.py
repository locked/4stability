#!/usr/bin/python
from optparse import OptionParser
import os
import sys
import time
import csv
import datetime

import motor
import adxl345
import hcsr04


parser = OptionParser()
parser.add_option("-p", "--p", dest="p", help="")
(options, args) = parser.parse_args()


m = motor.Motor(debug=False)
accel = adxl345.ADXL345()
dist = hcsr04.HCSR04()

m.init()

speed_percent = 0.0

try:
	lines = []
	while (True):
		distance = dist.measure()
		axis = accel.getAxes()

		speed_percent += 0.1
		if speed_percent > 30: # max 34
			break
		pos = m.set_speed(speed_percent/100.0)

		ts = datetime.datetime.utcnow().strftime('%Y-%m-%d_%H:%M:%S_%f')

		line = []
		line.append(ts)
		line.append(axis['x'])
		line.append(axis['y'])
		line.append(axis['z'])

		line.append(round(distance,2))

		line.append(round(speed_percent,2))
		line.append(pos)
		lines.append(line)
		time.sleep(0.005)
except Exception as e:
	print e
finally:
	pos = m.set_speed(5)
	header = ["datetime", "x", "y", "z", "d", "speed", "speed_real"]
	ts = datetime.datetime.utcnow().strftime('%Y-%m-%d_%H:%M:%S_%f')
	with open('results/'+ts+'.csv', 'wb') as csvfile:
		spamwriter = csv.writer(csvfile, delimiter='	', quotechar='"', quoting=csv.QUOTE_MINIMAL)
		spamwriter.writerow(header)
		for line in lines:
			spamwriter.writerow(line)
	m.reset()
