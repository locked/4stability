#!/usr/bin/python
from optparse import OptionParser
import os
import sys
import time
import curses
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

speed_percent = 0

stdscr = curses.initscr()

try:
	stdscr.nodelay(1)
	lastt = 0
	previous_error = 0
	integral = 0
	derivative = 0
	speed_percent = 10
	diff_speed = 0
	error = 0
	dt = 0
	Kp = 0.0003
	Ki = 0
	Kd = 0
	start_time = time.time()*100000
	lines = []
	while (True):
		distance = 0 #dist.measure()
		axis = accel.getAxes()

		if lastt > 0:
			error = 0 - axis['y']
			dt = time.time()*1000 - lastt
			integral = integral + error * dt
			derivative = (error - previous_error)/dt
			diff_speed = Kp * error + Ki * integral + Kd * derivative
			previous_error = error
		lastt = time.time()*100000

		speed_percent = speed_percent - diff_speed
		if speed_percent > 23:
			speed_percent = 23
		if speed_percent < 0:
			speed_percent = 0
		pos = m.set_speed(speed_percent/100.0)

		stdscr.addstr(2, 8, "Accelero:")
		stdscr.addstr(4, 9, "[                             ]")
		stdscr.addstr(4, 10, "x:%.2f" % axis['x'])
		stdscr.addstr(4, 20, "y:%.2f" % axis['y'])
		stdscr.addstr(4, 30, "z:%.2f" % axis['z'])

		stdscr.addstr(6, 8, "Distance:")
		stdscr.addstr(8, 9, "[%.1f]" % (distance))

		stdscr.addstr(10, 8, "Motor:")
		stdscr.addstr(12, 9, "[%d%% (%d)]" % (speed_percent, pos))

		stdscr.addstr(14, 8, "PID:")
		stdscr.addstr(15, 9, "[ERR:%.3f INT:%.3f DER:%.3f DT:%.3f DIFFSPEED:%.3f]" % (error, integral, derivative, dt, diff_speed))
		stdscr.refresh()

		line = []
		ts = datetime.datetime.utcnow().strftime('%Y-%m-%d_%H:%M:%S_%f')
		line.append(ts)
		reltime = time.time()*100000 - start_time
		line.append(reltime)
		line.append(round(speed_percent,2))
		line.append(axis['x'])
		line.append(axis['y'])
		line.append(axis['z'])
		line.append(round(distance,2))
		line.append(error)
		line.append(integral)
		line.append(derivative)
		line.append(dt)
		line.append(diff_speed)
		lines.append(line)

		time.sleep(0.01)
except Exception as e:
	print "Error"
	print e
finally:
	print "Ending"
	m.reset()
	curses.endwin()

	# Save in CSV
	header = ["datetime", "reltime", "speed", "x", "y", "z", "d", "error", "integral", "derivative", "dt", "diff_speed"]
	ts = datetime.datetime.utcnow().strftime('%Y-%m-%d_%H:%M:%S_%f')
	with open('results/PID_%s_Kp%f_Ki%f_Kd%f.csv' % (ts, Kp, Ki, Kd), 'wb') as csvfile:
		spamwriter = csv.writer(csvfile, delimiter='	', quotechar='"', quoting=csv.QUOTE_MINIMAL)
		spamwriter.writerow(header)
		for line in lines:
			spamwriter.writerow(line)

