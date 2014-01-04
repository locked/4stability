#!/usr/bin/python
from optparse import OptionParser
import os
import sys
import time
import csv
import datetime

import adxl345
import hcsr04

def experiment(bwrate, range, duration):
	try:
		print 'start experiment:'+str(bwrate)+'@'+str(range)
		lines = []
		accel = adxl345.ADXL345(bwrate=bwrate, range=range)
		ts_start = time.time()
		while (True):
			distance = 0 #dist.measure()
			axis = accel.getAxes()

			ts = datetime.datetime.utcnow().strftime('%Y-%m-%d_%H:%M:%S_%f')
			ts_micro = int(time.time()*1000.0)
			if time.time() - ts_start > duration:
				break

			line = []
			line.append(ts)
			line.append(round(ts_micro,2))
			line.append(axis['x'])
			line.append(axis['y'])
			line.append(axis['z'])

			line.append(round(distance,2))

			lines.append(line)
			time.sleep(0.005)
	except Exception as e:
		print e
	finally:
		header = ["datetime", "speed", "x", "y", "z", "d"]
		ts = datetime.datetime.utcnow().strftime('%Y-%m-%d_%H:%M:%S_%f')
		fn = 'results/'+ts+'_'+str(duration)+'-'+str(bwrate)+'@'+str(range)+'.csv'
		print fn
		with open(fn, 'wb') as csvfile:
			spamwriter = csv.writer(csvfile, delimiter='	', quotechar='"', quoting=csv.QUOTE_MINIMAL)
			spamwriter.writerow(header)
			for line in lines:
				spamwriter.writerow(line)

#bwrates = [adxl345.ADXL345.BW_RATE_1600HZ, adxl345.ADXL345.BW_RATE_800HZ, adxl345.ADXL345.BW_RATE_200HZ, adxl345.ADXL345.BW_RATE_100HZ, adxl345.ADXL345.BW_RATE_50HZ, adxl345.ADXL345.BW_RATE_25HZ]
bwrates = [adxl345.ADXL345.BW_RATE_1600HZ, adxl345.ADXL345.BW_RATE_25HZ]
#ranges = [adxl345.ADXL345.RANGE_2G, adxl345.ADXL345.RANGE_4G, adxl345.ADXL345.RANGE_8G, adxl345.ADXL345.RANGE_16G]
ranges = [adxl345.ADXL345.RANGE_2G]

for bwrate in bwrates:
	for range in ranges:
		experiment(bwrate, range, 10)

