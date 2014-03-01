#!/usr/bin/python
from optparse import OptionParser
import os
import sys
import time
import termios
import fcntl
import motor

parser = OptionParser()
parser.add_option("-a", "--action", dest="action", help="reset/manual")
(options, args) = parser.parse_args()


m = motor.Motor(0)


if options.action == "reset":
	m.reset()

elif options.action == "cycle":
	m.init()
	speed_percent = 0
	while speed_percent < 30:
		speed_percent += 1
	while speed_percent > 0:
		speed_percent -= 1
	m.reset()

elif options.action == "manual":
	m.init()

	# Terminal init stuff found on stackoverflow (SlashV)
	fd = sys.stdin.fileno()
	oldterm = termios.tcgetattr(fd)
	newattr = termios.tcgetattr(fd)
	newattr[3] = newattr[3] & ~termios.ICANON & ~termios.ECHO
	termios.tcsetattr(fd, termios.TCSANOW, newattr)
	oldflags = fcntl.fcntl(fd, fcntl.F_GETFL)
	fcntl.fcntl(fd, fcntl.F_SETFL, oldflags | os.O_NONBLOCK)

	try:
		speed_percent = 0
		while (True):
			try:
				c = sys.stdin.read(1)
			except IOError:
				c = ''
			if c == "-":
				speed_percent = speed_percent - 1 if speed_percent > 1 else 0
			elif c == "+":
				speed_percent = speed_percent + 1 if speed_percent < 100 else 0
			pos = m.set_speed(speed_percent/100.0)
			sys.stdout.write("\r%d%% (%d)" % (speed_percent, pos))
			sys.stdout.flush()
			#time.sleep(.1)
	except: pass
	finally:
		# Reset terminal
		termios.tcsetattr(fd, termios.TCSAFLUSH, oldterm)
		fcntl.fcntl(fd, fcntl.F_SETFL, oldflags)
		m.reset()

