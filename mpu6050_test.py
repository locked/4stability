#!/usr/bin/python

import math
import mpu6050
import time
import sys


if __name__ == "__main__":
	mpu = mpu6050.MPU6050()
	mpu.dmpInitialize()
	mpu.setDMPEnabled(True)

	packetSize = mpu.dmpGetFIFOPacketSize()

	while True:
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

			sys.stdout.write("\r[Yaw:%.2f Pitch:%.2f Roll:%.2f]" % (yaw, pitch, roll))
			sys.stdout.flush()
			#time.sleep(0.2)

