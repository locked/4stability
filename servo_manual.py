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

pos = servoMin
try:
  while (True):
    try:
      c = sys.stdin.read(1)
    except IOError:
      c = ''
    if c == "-":
      pos -= 10
    elif c == "+":
      pos += 10
    sys.stdout.write("\r%d" % pos)
    sys.stdout.flush()
    pwm.setPWM(0, 0, pos)
    #time.sleep(.1)
except: pass
finally:
  # Reset terminal
  termios.tcsetattr(fd, termios.TCSAFLUSH, oldterm)
  fcntl.fcntl(fd, fcntl.F_SETFL, oldflags)

