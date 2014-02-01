#!/usr/bin/python
from optparse import OptionParser
import os
import sys
import time
import math
import csv
import datetime

import motor
import adxl345
import hcsr04
import mpu6050

#parser = OptionParser()
#parser.add_option("-p", "--p", dest="p", help="")
#(options, args) = parser.parse_args()

m = motor.Motor(debug=False)
dist = hcsr04.HCSR04()

m.init()

def experiment(bwrate, range, max_speed):
	try:
		print 'start experiment:'+str(bwrate)+'@'+str(range)
		lines = []
		speed_percent = 0.0
		start_timeout = None
		start_time = time.time()*100000
		accel = adxl345.ADXL345(bwrate=bwrate, range=range)
		mpu_mode = 'advanced'
		if mpu_mode == 'basic':
			mpu = mpu6050.MPU6050()
			mpu.init()
		else:
			mpu = mpu6050.MPU6050()
			mpu.dmpInitialize()
			mpu.setDMPEnabled(True)
			packetSize = mpu.dmpGetFIFOPacketSize()
		while (True):
			distance = dist.measure()
			axis = accel.getAxes()
			yaw = 0
			pitch = 0
			roll = 0
			if mpu_mode == 'basic':
				data = mpu.readall()
				gyro = data['gyro_scaled']
				mpu_accel = data['accel_scaled']
			else:
				gyro = {'x':0, 'y':0, 'z':0}
				mpu_accel = {'x':0, 'y':0, 'z':0}
				# Get INT_STATUS byte
				mpuIntStatus = mpu.getIntStatus()

				if mpuIntStatus >= 2: # check for DMP data ready interrupt (this should happen frequently) 
					# get current FIFO count
					fifoCount = mpu.getFIFOCount()
					if fifoCount == 1024:
						# reset so we can continue cleanly
						mpu.resetFIFO()
						print('FIFO overflow!')

					# wait for correct available data length, should be a VERY short wait
					fifoCount = mpu.getFIFOCount()
					while fifoCount < packetSize:
						fifoCount = mpu.getFIFOCount()

					result = mpu.getFIFOBytes(packetSize)
					q = mpu.dmpGetQuaternion(result)
					g = mpu.dmpGetGravity(q)
					ypr = mpu.dmpGetYawPitchRoll(q, g)

					yaw = ypr['yaw'] * 180 / math.pi
					pitch = ypr['pitch'] * 180 / math.pi
					roll = ypr['roll'] * 180 / math.pi

					# track FIFO count here in case there is > 1 packet available
					# (this lets us immediately read more without waiting for an interrupt)        
					fifoCount -= packetSize  

					#sys.stdout.write("\r[Yaw:%.2f Pitch:%.2f Roll:%.2f]" % (yaw, pitch, roll))
					#sys.stdout.flush()


			if start_timeout is None:
				speed_percent += 0.05
				print speed_percent
			else:
				print time.time() - start_timeout
			if speed_percent > max_speed: # max 34
				speed_percent = max_speed
				start_timeout = time.time()
				#break
			if start_timeout is not None and (time.time() - start_timeout) > 5:
				break
			pos = m.set_speed(speed_percent/100.0)

			ts = datetime.datetime.utcnow().strftime('%Y-%m-%d_%H:%M:%S_%f')

			line = []
			line.append(ts)
			reltime = time.time()*100000 - start_time
			line.append(reltime)
			line.append(round(speed_percent,2))
			line.append(axis['x'])
			line.append(axis['y'])
			line.append(axis['z'])

			line.append(mpu_accel['x'])
			line.append(mpu_accel['y'])
			line.append(mpu_accel['z'])

			line.append(gyro['x'])
			line.append(gyro['y'])
			line.append(gyro['z'])

			line.append(yaw)
			line.append(pitch)
			line.append(roll)

			line.append(round(distance,2))

			line.append(pos)
			lines.append(line)
			time.sleep(0.05)
	except Exception as e:
		print e
	finally:
		m.set_speed(0)
		#time.sleep(0.1)
		header = ["datetime", "reltime", "speed", "adxl_x", "adxl_y", "adxl_z", "mpu_x", "mpu_y", "mpu_z", "gx", "gy", "gz", "yaw", "pitch", "roll", "d", "speed_real"]
		ts = datetime.datetime.utcnow().strftime('%Y-%m-%d_%H:%M:%S_%f')
		with open('results/'+ts+'_'+str(max_speed)+'-'+str(bwrate)+'@'+str(range)+'.csv', 'wb') as csvfile:
			spamwriter = csv.writer(csvfile, delimiter='	', quotechar='"', quoting=csv.QUOTE_MINIMAL)
			spamwriter.writerow(header)
			for line in lines:
				spamwriter.writerow(line)

#bwrates = [adxl345.ADXL345.BW_RATE_1600HZ, adxl345.ADXL345.BW_RATE_800HZ, adxl345.ADXL345.BW_RATE_200HZ, adxl345.ADXL345.BW_RATE_100HZ, adxl345.ADXL345.BW_RATE_50HZ, adxl345.ADXL345.BW_RATE_25HZ]
#bwrates = [adxl345.ADXL345.BW_RATE_25HZ, adxl345.ADXL345.BW_RATE_100HZ]
bwrates = [adxl345.ADXL345.BW_RATE_100HZ]
#ranges = [adxl345.ADXL345.RANGE_2G, adxl345.ADXL345.RANGE_4G, adxl345.ADXL345.RANGE_8G, adxl345.ADXL345.RANGE_16G]
ranges = [adxl345.ADXL345.RANGE_2G]
for bwrate in bwrates:
	for range in ranges:
		#experiment(bwrate, range, 47)
		#experiment(bwrate, range, 21.4)
		experiment(bwrate, range, 22)
		time.sleep(3)

m.reset()

