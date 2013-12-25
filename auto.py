#!/usr/bin/python
from optparse import OptionParser
import os
import sys
import time
import curses

import motor
import adxl345


parser = OptionParser()
parser.add_option("-p", "--p", dest="p", help="")
(options, args) = parser.parse_args()


m = motor.Motor(debug=False)
accel = adxl345.ADXL345()

#m.init()

speed_percent = 0

stdscr = curses.initscr()

try:
	stdscr.nodelay(1)
	while (True):
		axis = accel.getAxes()
		#pos = m.set_speed(speed_percent/100.0)

		cn = stdscr.getch(0, 0)
		c = chr(cn) if cn>0 and cn<255 else ''
		if c == "-":
			speed_percent = speed_percent - 1 if speed_percent > 1 else 0
		elif c == "+":
			speed_percent = speed_percent + 1 if speed_percent < 100 else 0

		pos = speed_percent/100.0

		stdscr.addstr(2, 8, "Accelero:")
		stdscr.addstr(4, 9, "[                             ]")
		stdscr.addstr(4, 10, "x:%.2f" % axis['x'])
		stdscr.addstr(4, 20, "y:%.2f" % axis['y'])
		stdscr.addstr(4, 30, "z:%.2f" % axis['z'])

		stdscr.addstr(7, 8, "Motor:")
		stdscr.addstr(9, 9, "[%d%% (%d)]" % (speed_percent, pos))
		stdscr.refresh()
		time.sleep(0.01)
except Exception as e:
	print e
finally:
	m.reset()
	curses.endwin()

