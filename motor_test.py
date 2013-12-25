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


# Terminal init stuff found on stackoverflow (SlashV)
fd = sys.stdin.fileno()
oldterm = termios.tcgetattr(fd)
newattr = termios.tcgetattr(fd)
newattr[3] = newattr[3] & ~termios.ICANON & ~termios.ECHO
termios.tcsetattr(fd, termios.TCSANOW, newattr)
oldflags = fcntl.fcntl(fd, fcntl.F_GETFL)
fcntl.fcntl(fd, fcntl.F_SETFL, oldflags | os.O_NONBLOCK)


m = motor.Motor()

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

	try:
		speed_percent = 0
		while (True):
			try:
				c = sys.stdin.read(1)
			except IOError:
				c = ''
			if c == "-":
				speed_percent -= 1
			elif c == "+":
				speed_percent += 1
			sys.stdout.write("\r%d" % speed_percent)
			sys.stdout.flush()
			m.set_speed(speed_percent)
			#time.sleep(.1)
		m.reset()
	except: pass
	finally:
		# Reset terminal
		termios.tcsetattr(fd, termios.TCSAFLUSH, oldterm)
		fcntl.fcntl(fd, fcntl.F_SETFL, oldflags)

