#!/usr/bin/python
import time
import hcsr04

dist = hcsr04.HCSR04()

try:
	while True:
		distance = dist.measure()
		print "Distance:%.1f" % distance
		time.sleep(0.2)
except:
	pass
finally:
	dist.cleanup()
