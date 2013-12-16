#!/usr/bin/python

import mpu6050
import time
import sys


if __name__ == "__main__":
	mpu = mpu6050.MPU6050()

	mpu.init() 
	while(True):
		data = mpu.readall()
		gyro = data['gyro_scaled']
		accel = data['accel_scaled']
		sys.stdout.write("\rGYRO:[x:%.2f y:%.2f z:%.2f] ACCEL:[x:%.2f y:%.2f z:%.2f]" % (gyro['x'], gyro['y'], gyro['z'], accel['x'], accel['y'], accel['z']))
		sys.stdout.flush()
		time.sleep(0.2)

