#!/usr/bin/python
from optparse import OptionParser
import os
import sys
import time
import math
import curses
import csv
import datetime

import motor
import adxl345
import hcsr04
import mpu6050


parser = OptionParser()
parser.add_option("-p", "--p", dest="p", help="")
(options, args) = parser.parse_args()

enable_motor = True
enable_mpu_dmp = False
enable_curse = True

if enable_motor:
	m = motor.Motor(debug=False)
	m.init()

accel = adxl345.ADXL345(bwrate=adxl345.ADXL345.BW_RATE_25HZ, range=adxl345.ADXL345.RANGE_2G)
dist = hcsr04.HCSR04()

speed_percent = 0

if enable_curse:
	stdscr = curses.initscr()

try:
	if enable_curse:
		stdscr.nodelay(1)
	lastt = 0
	previous_error = 0
	integral = 0
	derivative = 0
	speed_percent = 10
	diff_speed = 0
	error = 0
	dt = 0
	Kp = 0.001
	Ki = 0.00000
	Kd = 0.002
	KpDiff = 0.0001
	KiDiff = 0.00001
	KdDiff = 0.0001
	target = 0
	start_time = time.time()*100000
	lines = []
	speed_percent = 18
	if enable_motor:
		pos = m.set_speed(speed_percent/100.0)
	time.sleep(3)
	ys = []
	angle_rad = 0
	axis = {}
	mpu = mpu6050.MPU6050()
	mpu.initialize()
	mpu.setRate(39) # 1khz / (1 + 4) = 200 Hz [9 = 100 Hz]
	#mpu.dmpInitialize()
	#mpu.setDMPEnabled(True)
	while (True):
		distance = 0 #dist.measure()
		axis = accel.getAxes()
		data = mpu.readall()
		gyro = data['gyro_scaled']
		mpu_accel = data['accel_scaled']

		#(axis['x'], axis['y'], axis['z'], fifocount) = mpu.getYPR()
		#ys.append(axis['y'])
		#if len(ys) > 3: ys.pop(0)
		#angle_rad = axis['y'] #sum(ys) / float(len(ys))

		cn = ''
		if enable_curse:
			cn = stdscr.getch(0, 0)
		c = chr(cn) if cn>0 and cn<255 else ''
		if c == 'q': Kp = Kp + KpDiff
		if c == 'a': Kp = Kp - KpDiff if Kp - KpDiff >= 0 else 0
		if c == 'w': Ki = Ki + KiDiff
		if c == 's': Ki = Ki - KiDiff if Ki - KiDiff >= 0 else 0
		if c == 'e': Kd = Kd + KdDiff
		if c == 'd': Kd = Kd - KdDiff if Kd - KdDiff >= 0 else 0

		angle = 0
		atan = 0
		asin = 0
		p1 = 0
		p2 = 0
		if lastt > 0:
			dt = (time.time()*1000 - lastt) / 1000

			# angle
			p1 = 0.9
			p2 = 1 - p1
			atan = math.atan(axis['y']/axis['z']) if axis['z'] <> 0 else 0
			y = axis['y']*0.004
			if y>1: y = 1
			if y<-1: y = -1
			asin = -math.asin(y)
			angle_rad = p1 * (angle_rad - (gyro['y']/20) * dt) + p2 * atan
			angle = angle_rad * 28.66

			# PID
			error = target - angle
			integral = integral + error * dt
			derivative = (error - previous_error)/dt
			#speed_percent = Kp * error + Ki * integral + Kd * derivative
			diff_speed = Kp * error + Ki * integral + Kd * derivative
			previous_error = error
		lastt = time.time()*1000

		speed_percent = speed_percent + diff_speed
		if speed_percent > 25:
			speed_percent = 25
		if speed_percent < 10:
			speed_percent = 10
		pos = 0
		if enable_motor:
			pos = m.set_speed(speed_percent/100.0)

		if enable_curse:
			stdscr.addstr(2, 8, "ADXL:")
			stdscr.addstr(4, 9, "[                             ]")
			stdscr.addstr(4, 10, "x:%.2f" % axis['x'])
			stdscr.addstr(4, 20, "y:%.2f" % axis['y'])
			stdscr.addstr(4, 30, "z:%.2f" % axis['z'])

			stdscr.addstr(5, 8, "MPU gyro + accel:")
			stdscr.addstr(6, 9, "[                             ]")
			stdscr.addstr(6, 10, "x:%.2f" % gyro['x'])
			stdscr.addstr(6, 20, "y:%.2f" % gyro['y'])
			stdscr.addstr(6, 30, "z:%.2f" % gyro['z'])

			stdscr.addstr(7, 9, "[                             ]")
			stdscr.addstr(7, 10, "x:%.2f" % mpu_accel['x'])
			stdscr.addstr(7, 20, "y:%.2f" % mpu_accel['y'])
			stdscr.addstr(7, 30, "z:%.2f" % mpu_accel['z'])

			stdscr.addstr(9, 9, "Distance:[%.1f]" % (distance))

			stdscr.addstr(10, 8, "Motor:")
			stdscr.addstr(12, 9, "[%.4f%% (%d)]" % (speed_percent, pos))

			stdscr.addstr(14, 8, "PID:")
			stdscr.addstr(15, 9, "[DT:%.3f]" % (dt))
			stdscr.addstr(16, 9, "[Erreur:%.3f] [Avgy:%.3f] [Atan:%.3f] [Asin:%.3f] [P1:%.3f] [P2:%.3f]" % (error, angle_rad, atan, asin, p1, p2))
			stdscr.addstr(17, 9, "[Integral:%.3f Derivative:%.3f]" % (integral, derivative))
			stdscr.addstr(18, 9, "[DIFFSPEED:%.3f]" % (diff_speed))
			stdscr.addstr(19, 9, "[Kp*E:%.6f]" % (Kp * error))
			stdscr.addstr(20, 9, "[Ki*E:%.6f]" % (Ki * integral))
			stdscr.addstr(21, 9, "[Kd*E:%.6f]" % (Kd * derivative))
			stdscr.addstr(22, 9, "[Kp:%.6f]" % (Kp))
			stdscr.addstr(23, 9, "[Ki:%.6f]" % (Ki))
			stdscr.addstr(24, 9, "[Kd:%.6f]" % (Kd))
			if enable_mpu_dmp: stdscr.addstr(26, 9, "[fifo_count:%d]" % (fifocount))
			stdscr.refresh()

		line = []
		ts = datetime.datetime.utcnow().strftime('%Y-%m-%d_%H:%M:%S_%f')
		line.append(ts)
		reltime = time.time()*100000 - start_time
		line.append(reltime)
		line.append(pos)
		line.append(axis['x'])
		line.append(axis['y'])
		line.append(axis['z'])
		line.append(gyro['x'])
		line.append(gyro['y'])
		line.append(gyro['z'])
		line.append(mpu_accel['x'])
		line.append(mpu_accel['y'])
		line.append(mpu_accel['z'])
		line.append(round(distance,2))
		line.append(round(atan*28.66,2))
		line.append(round(asin*28.66,2))
		line.append(angle)
		line.append(angle_rad)
		line.append(error)
		line.append(integral)
		line.append(derivative)
		line.append(Kp)
		line.append(Ki)
		line.append(Kd)
		line.append(dt)
		line.append(diff_speed)
		lines.append(line)

		time.sleep(0.05)
except Exception as e:
	if enable_curse:
		curses.endwin()
	print "Error"
	print e
finally:
	print "Ending"
	if enable_motor:
		m.reset()
	if enable_curse:
		try:
			curses.endwin()
		except: pass

	# Save in CSV
	header = ["datetime", "reltime", "speed", "adxlx", "adxly", "adxlz", "gyrox", "gyroy", "gyroz", "mpu_accelx", "mpu_accely", "mpu_accelz", "distance", "atan", "asin", "angle", "angle_rad", "error", "integral", "derivative", "Kp", "Ki", "Kd", "dt", "diff_speed"]
	ts = datetime.datetime.utcnow().strftime('%Y-%m-%d_%H:%M:%S_%f')
	with open('results/PID_%s_Kp%f_Ki%f_Kd%f.csv' % (ts, Kp, Ki, Kd), 'wb') as csvfile:
		spamwriter = csv.writer(csvfile, delimiter='	', quotechar='"', quoting=csv.QUOTE_MINIMAL)
		spamwriter.writerow(header)
		for line in lines:
			spamwriter.writerow(line)

