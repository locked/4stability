#!/usr/bin/python
import os
import sys
import time
import termios
import fcntl
from Adafruit_PWM_Servo_Driver import PWM

# Terminal init stuff found on stackoverflow (SlashV)
fd = sys.stdin.fileno()
oldterm = termios.tcgetattr(fd)
newattr = termios.tcgetattr(fd)
newattr[3] = newattr[3] & ~termios.ICANON & ~termios.ECHO
termios.tcsetattr(fd, termios.TCSANOW, newattr)
oldflags = fcntl.fcntl(fd, fcntl.F_GETFL)
fcntl.fcntl(fd, fcntl.F_SETFL, oldflags | os.O_NONBLOCK)

# Init PWM
pwm = PWM(0x40, debug=True)
pwm.setPWMFreq(60)

# min/max found by trial and error:
servoMin = 130
servoMax = 610
servoInit = 185
servoMotorStart = 245

def init(pwm, servoInit, sleep=3):
	print "Init...",
	pwm.setPWM(0, 0, servoInit)
	time.sleep(sleep)
	pwm.setPWM(1, 0, servoInit)
	time.sleep(sleep)
	print "Done"

init(pwm, servoInit)

pos1 = servoInit
pos2 = servoInit
try:
  while (True):
    try:
      c = sys.stdin.read(1)
    except IOError:
      c = ''
    if c == "a":
      pos1 -= 10
    elif c == "q":
      pos1 += 10
    if c == "s":
      pos2 -= 10
    elif c == "w":
      pos2 += 10
    sys.stdout.write("\r%d / %d" % (pos1, pos2))
    sys.stdout.flush()
    pwm.setPWM(0, 0, pos1)
    pwm.setPWM(1, 0, pos2)
    #time.sleep(.1)
except: pass
finally:
  # Reset terminal
  termios.tcsetattr(fd, termios.TCSAFLUSH, oldterm)
  fcntl.fcntl(fd, fcntl.F_SETFL, oldflags)
  init(pwm, servoInit, 0)

