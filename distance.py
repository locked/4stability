#!/usr/bin/python
import time
import RPi.GPIO as GPIO

pin_gpio_trigger = 23
pin_gpio_echo    = 24

GPIO.setmode(GPIO.BCM)
GPIO.setup(pin_gpio_trigger, GPIO.OUT)
GPIO.setup(pin_gpio_echo, GPIO.IN)
GPIO.output(pin_gpio_trigger, False)

time.sleep(0.5)

def measure():
	GPIO.output(pin_gpio_trigger, True)
	time.sleep(0.00001)
	GPIO.output(pin_gpio_trigger, False)
	start = time.time()
	while GPIO.input(pin_gpio_echo)==0:
		start = time.time()
	while GPIO.input(pin_gpio_echo)==1:
		stop = time.time()

	elapsed = stop-start
	distance = (elapsed * 34000) / 2
	return distance

try:
	while True:
		distance = measure()
		print "Distance:%.1f" % distance
		time.sleep(0.2)
except:
	pass
finally:
	print "Cleanup GPIO"
	GPIO.cleanup()
