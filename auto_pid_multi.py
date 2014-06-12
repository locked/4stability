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



def curses_bar(stdscr, y, x, percent, val):
	max_rel = 50
	for i in range(0, max_rel):
		c = "X" if percent >= (max_rel/100.0) else "."
		try:
			stdscr.addstr(int(y), int(x + i), c)
		except:
			pass
	try:
		stdscr.addstr(y, int(x + i), "  %s" % val)
	except:
		pass


parser = OptionParser()
parser.add_option("-p", "--p", dest="p", help="")
(options, args) = parser.parse_args()


enable_motor = True
enable_mpu_dmp = False
enable_curse = True
RAD_TO_DEG = 57.3
DEG_TO_RAD = 1 / RAD_TO_DEG
ACCEL_SF = 0.004
base_sleep_time = 0.01 #25

BALANCE_PITCH = 0
SPEED_TO_FORCE = 1

#motor0 : N / motor1 : S
print "Init motors...",
if enable_motor:
	motors = [motor.Motor(0, debug=False).init(), motor.Motor(1, debug=False).init()]
print "Done"

print "Init accels...",
accel = adxl345.ADXL345(bwrate=adxl345.ADXL345.BW_RATE_25HZ, range=adxl345.ADXL345.RANGE_2G)
accel_init = {'x':20, 'y':20, 'z':0}
dist  = hcsr04.HCSR04()
mpu   = mpu6050.MPU6050()
mpu.initialize()
mpu.setRate(39) # 1khz / (1 + 4) = 200 Hz [9 = 100 Hz]
#mpu_init = {'x':0.10, 'y':0, 'z':0}
mpu_init = {'x':0.07, 'y':0.01, 'z':0}
#mpu.dmpInitialize()
#mpu.setDMPEnabled(True)
print "Done"

# Init gyro et angle
print "Init gyro offset...",
gyro_init = {}
for i in ['x', 'y', 'z']: gyro_init[i] = 0
count = 0
max_count = 2 / base_sleep_time
while count < max_count:
	data = mpu.readall()
	#print "gyro_init:[%.2f:%.2f:%.2f]" % (data['gyro_scaled']['x'], data['gyro_scaled']['y'], data['gyro_scaled']['z'])
	for i in ['x', 'y', 'z']: gyro_init[i] += data['gyro_scaled'][i]
	count += 1
	time.sleep(base_sleep_time)
for i in ['x', 'y', 'z']: gyro_init[i] /= count
print "Done. Iterations:[%d] gyro_init:[%.2f:%.2f:%.2f]" % (count, gyro_init['x'], gyro_init['y'], gyro_init['z'])
axis = accel.getAxes()
angle_rad = math.atan(axis['y']/axis['z']) if axis['z'] <> 0 else 0
#sys.exit(0)

try:
	lastt = 0
	previous_error2 = 0
	integral = 0
	derivative = 0
	integral2 = 0
	derivative2 = 0
	
	diff_speed = 0
	max_speed = 0.20
	error = 0
	error2 = 0
	dt_ms = 0
	
	Kp = 0.6
	Ki = 0
	Kd = 0.00
	
	Kp2 = 0.08
	Ki2 = 0.00001
	Kd2 = 0.00
	
	KpDiff = 0.005
	KiDiff = 0.00001
	KdDiff = 0.00001
	target_deg = 0
	start_time = time.time()*1000000 # en us
	lines = []
	pid_output = 0
	pid_output2 = 0
	avg_speed = 6
	motor1_speed = 0
	motor2_speed = 0
	speed_percent = avg_speed
	pitch_offset = 0
	if enable_motor:
		print "Setup initial motor speed to:[%.2f]" % float(speed_percent),
		for m in motors:
			m.set_speed(speed_percent/100.0)
		time.sleep(1)
		print "Done"

	if enable_curse:
		stdscr = curses.initscr()
		stdscr.nodelay(1)

	ys = []
	#angle_rad = 0
	axis = {}
	while (True):
		init_time = time.time()
		
		distance = 0 #dist.measure()
		axis = accel.getAxes()
		for i in ['x', 'y', 'z']: axis[i] -= accel_init[i]
		data = mpu.readall()
		gyro = data['gyro_scaled']
		for i in ['x', 'y', 'z']: gyro[i] -= gyro_init[i] # Adjust gyro with initial offset
		mpu_accel = data['accel_scaled']
		for i in ['x', 'y', 'z']: mpu_accel[i] -= mpu_init[i]

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
		if c == 'r': Kp2 = Kp2 + KpDiff
		if c == 'f': Kp2 = Kp2 - KpDiff if Kp2 - KpDiff >= 0 else 0
		if c == 't': Ki2 = Ki2 + KiDiff
		if c == 'g': Ki2 = Ki2 - KiDiff if Ki2 - KiDiff >= 0 else 0
		if c == 'y': Kd2 = Kd2 + KdDiff
		if c == 'h': Kd2 = Kd2 - KdDiff if Kd2 - KdDiff >= 0 else 0
		
		angle_deg = 0
		atan_rad  = 0

		p1 = 0
		p2 = 0
		target_angleRate = 0
		pitch_offset_force = 0
		if lastt > 0:
			dt_ms = (time.time()*1000 - lastt)

			# angle
			p1 = 0.98
			p2 = 1 - p1
			#atan_rad = math.atan(axis['y']/axis['z']) if axis['z'] <> 0 else 0
			atan_rad = math.atan(axis['x']/axis['z']) if axis['z'] <> 0 else 0
			angle_rad = p1 * (angle_rad - (gyro['y'] * DEG_TO_RAD * (dt_ms/1000))) + p2 * atan_rad
			angle_deg = angle_rad * RAD_TO_DEG
			
			
			# PID1 : get target angle rate
			error = target_deg - angle_deg
			integral += error * dt_ms
			max_integral = 1000
			if integral > max_integral: integral = max_integral
			if integral < (0 - max_integral): integral = (0 - max_integral)
			derivative = gyro['y']
			pid_output = Kp * error + Ki * integral + Kd * derivative
			if pid_output > 60: pid_output = 60
			if pid_output < 0: pid_output = 0
			
			target_angleRate = pid_output
			actual_angleRate = gyro['y']

			# Only ONE PID:
			pitch_offset = pid_output

			# PID2 : get pitch_offset
			error2 = 0
			integral2 = 0
			derivative2 = 0
			pid_output2 = 0
			previous_error2 = 0
			pitch_offset_force = 0
			pitch_offset_speedRaw = 0
			"""
			error2 = target_angleRate - actual_angleRate
			integral2 += error2 * dt_ms
			if integral2 > max_integral: integral2 = max_integral
			if integral2 < (0 - max_integral): integral2 = (0 - max_integral)
			derivative2 = error2 - previous_error2
			pid_output2 = Kp2 * error2 + Ki2 * integral2 + Kd2 * derivative2
			previous_error2 = error2
			
			pitch_offset_force = pid_output2
			
			# Pseudo-Physical Model to get actual pitch_offset
			
			pitch_offset_speedRaw = pitch_offset_force / SPEED_TO_FORCE
			
			# Correct unbalanced CoG
			pitch_offset = pitch_offset_speedRaw # + BALANCE_PITCH
			"""



		lastt = time.time()*1000

		#if pitch_offset > 5:
		#	pitch_offset = 5
		#if pitch_offset < -5:
		#	pitch_offset = -5

		if enable_motor:
			# First motor
			motor1_speed = (avg_speed - pitch_offset)/100.0
			motors[0].set_speed(motor1_speed, 0, max_speed)
			# Second motor
			motor2_speed = ((avg_speed + pitch_offset)/100.0) # * 1.15 # - 0.012
			motors[1].set_speed(motor2_speed, 0, max_speed)

		if enable_curse:
			stdscr.addstr(2, 8, "ADXL:")
			stdscr.addstr(3, 9, "[                             ]")
			stdscr.addstr(3, 10, "x:%.2f" % axis['x'])
			stdscr.addstr(3, 20, "y:%.2f" % axis['y'])
			stdscr.addstr(3, 30, "z:%.2f" % axis['z'])

			stdscr.addstr(4, 8, "MPU gyro:")
			stdscr.addstr(5, 9, "[                             ]")
			stdscr.addstr(5, 10, "x:%.2f" % gyro['x'])
			stdscr.addstr(5, 20, "y:%.2f" % gyro['y'])
			stdscr.addstr(5, 30, "z:%.2f" % gyro['z'])

			stdscr.addstr(6, 8, "MPU accel:")
			stdscr.addstr(7, 9, "[                             ]")
			stdscr.addstr(7, 10, "x:%.2f" % mpu_accel['x'])
			stdscr.addstr(7, 20, "y:%.2f" % mpu_accel['y'])
			stdscr.addstr(7, 30, "z:%.2f" % mpu_accel['z'])

			#stdscr.addstr(9, 9, "Distance:[%.1f]" % (distance))

			stdscr.addstr(10, 8, "Motors:")
			for i, m in enumerate(motors):
				#stdscr.addstr(11+i, 9, "[%.4f%% (%d)]" % (m.speed_percent, m.position))
				curses_bar(stdscr, 11+i, 9, m.asked_speed_percent, "[%.4f%% / %.4f%% (%d)]" % (m.asked_speed_percent, m.speed_percent, m.position)) #stdscr.addstr(11+i, 9, "[%.4f%% (%d)]" % (m.speed_percent, m.position))

			stdscr.addstr(14, 8, "PID:")
			stdscr.addstr(15, 9, "[DT:%.3f]" % (dt_ms))
			stdscr.addstr(16, 9, "[Error:%.3f] [Error2:%.3f] [angle_rad:%.3f] [atan_rad:%.3f]" % (error, error2, angle_rad, atan_rad))
			stdscr.addstr(17, 9, "[Integral:%.3f Derivative:%.3f]" % (integral, derivative))
			stdscr.addstr(18, 9, "[DIFFSPEED:%.3f]" % (diff_speed))
			stdscr.addstr(19, 9, "[Kp*E:%.6f]" % (Kp * error))
			stdscr.addstr(20, 9, "[Ki*E:%.6f]" % (Ki * integral))
			stdscr.addstr(21, 9, "[Kd*E:%.6f]" % (Kd * derivative))
			stdscr.addstr(22, 9, "[Kp:%.6f]" % (Kp))
			stdscr.addstr(23, 9, "[Ki:%.6f]" % (Ki))
			stdscr.addstr(24, 9, "[Kd:%.6f]" % (Kd))
			stdscr.addstr(25, 9, "[PID OUTPUT:%.6f]" % (pid_output))
			#stdscr.addstr(26, 9, "[Kp2*E:%.6f]" % (Kp2 * error2))
			#stdscr.addstr(27, 9, "[Ki2*E:%.6f]" % (Ki2 * integral2))
			#stdscr.addstr(28, 9, "[Kd2*E:%.6f]" % (Kd2 * derivative2))
			#stdscr.addstr(29, 9, "[Kp2:%.6f]" % (Kp2))
			#stdscr.addstr(30, 9, "[Ki2:%.6f]" % (Ki2))
			#stdscr.addstr(31, 9, "[Kd2:%.6f]" % (Kd2))
			#stdscr.addstr(32, 9, "[PID OUTPUT2:%.6f]" % (pid_output2))
			#stdscr.addstr(33, 9, "[pitch_offset:%.6f]" % (pitch_offset))
			#if enable_mpu_dmp: stdscr.addstr(26, 9, "[fifo_count:%d]" % (fifocount))
			stdscr.refresh()

		# Data logging
		line = []
		ts = datetime.datetime.utcnow().strftime('%Y-%m-%d_%H:%M:%S_%f')
		line.append(ts)
		reltime = time.time()*1000000 - start_time
		line.append(reltime)
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
		line.append(round(atan_rad * RAD_TO_DEG,2))
		line.append(angle_deg)
		
		line.append(error)
		line.append(integral)
		line.append(derivative)
		line.append(Kp)
		line.append(Ki)
		line.append(Kd)
		line.append(pid_output)
		line.append(target_angleRate)
		
		line.append(error2)
		line.append(integral2)
		line.append(derivative2)
		line.append(Kp2)
		line.append(Ki2)
		line.append(Kd2)
		line.append(pid_output2)

		line.append(pitch_offset_force)
		line.append(pitch_offset)
		
		line.append(dt_ms)

		for m in motors: line.append(m.position)
		
		line.append(motor1_speed)
		line.append(motor2_speed)

		lines.append(line)

		# Sleep to reach target rate
		sleep_time = base_sleep_time - (time.time() - init_time)
		if sleep_time > 0:
			time.sleep(sleep_time)
except Exception as e:
	if enable_curse:
		curses.endwin()
	print "Error"
	print e
finally:
	print "Ending"
	if enable_motor:
		for m in motors:
			m.reset()
	if enable_curse:
		try:
			curses.endwin()
		except: pass

	# Save in CSV
	header = ["datetime", "reltime", "adxlx", "adxly", "adxlz", "gyrox", "gyroy", "gyroz", "mpu_accelx", "mpu_accely", "mpu_accelz", "distance", "atan", "angle", "error", "integral", "derivative", "Kp", "Ki", "Kd", "pid_output", "target_angleRate2", "error2", "integral2", "derivative2", "Kp2", "Ki2", "Kd2", "pid_output2", "pitch_offset_force", "pitch_offset", "dt", "m1_pos", "m2_pos", "m1_percent", "m2_percent"]
	for i, m in enumerate(motors):
		header.append("Motor%d" % i)
	ts = datetime.datetime.utcnow().strftime('%Y-%m-%d_%H:%M:%S_%f')
	with open('results/PID_%s_Kp%f_Ki%f_Kd%f.csv' % (ts, Kp, Ki, Kd), 'wb') as csvfile:
		spamwriter = csv.writer(csvfile, delimiter='	', quotechar='"', quoting=csv.QUOTE_MINIMAL)
		spamwriter.writerow(header)
		for line in lines:
			spamwriter.writerow(line)

