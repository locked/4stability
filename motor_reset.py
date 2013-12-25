#!/usr/bin/python

from Adafruit_PWM_Servo_Driver import PWM
import time
import sys

# Initialise the PWM device using the default address
pwm = PWM(0x40, debug=True)
pwm.setPWMFreq(60)                        # Set frequency to 60 Hz

servoMin = 150  # Min pulse length out of 4096
servoMax = 600  # Max pulse length out of 4096

print "Reset...",
pwm.setPWM(0, 0, servoMin)
print "Done"

