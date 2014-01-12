import time
import RPi.GPIO as GPIO


class HCSR04:
	pin_gpio_trigger = 23
	pin_gpio_echo    = 24

	def __init__(self):
		GPIO.setmode(GPIO.BCM)
		GPIO.setup(self.pin_gpio_trigger, GPIO.OUT)
		GPIO.setup(self.pin_gpio_echo, GPIO.IN)
		GPIO.output(self.pin_gpio_trigger, False)
		time.sleep(0.5)

	def measure(self):
		GPIO.output(self.pin_gpio_trigger, True)
		time.sleep(0.00001)
		GPIO.output(self.pin_gpio_trigger, False)
		tstart = time.time()
		start = time.time()
		while GPIO.input(self.pin_gpio_echo)==0 or time.time()-tstart>2:
			start = time.time()
		if time.time()-tstart>2:
			return 0
		while GPIO.input(self.pin_gpio_echo)==1:
			stop = time.time()
		elapsed = stop-start
		distance = (elapsed * 34000) / 2
		return distance

	def cleanup(self):
		print "Cleanup GPIO"
		GPIO.cleanup()
