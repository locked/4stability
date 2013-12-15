#!/usr/bin/python

from Adafruit_PWM_Servo_Driver import PWM
import time
import sys

# Initialise the PWM device using the default address
pwm = PWM(0x40, debug=True)
pwm.setPWMFreq(60)                        # Set frequency to 60 Hz

servoMin = 150  # Min pulse length out of 4096
servoMax = 600  # Max pulse length out of 4096
servoInit = 185
servoMotorStart = 245

print "Init...",
pwm.setPWM(0, 0, servoInit)
time.sleep(3)
print "Done"

print "Set %d" % servoMotorStart
pwm.setPWM(0, 0, servoMotorStart)
time.sleep(2)

for i in range(1,50):
	time.sleep(0.1)
	print "Set %d" % int(servoMotorStart+i)
	pwm.setPWM(0, 0, int(servoMotorStart+i))

pwm.setPWM(0, 0, servoMotorStart)
time.sleep(5)

pwm.setPWM(0, 0, servoMotorStart-5)
time.sleep(5)

print "Set minimum %d" % servoMin
pwm.setPWM(0, 0, servoMin)
