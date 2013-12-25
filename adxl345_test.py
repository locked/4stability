import adxl345
import sys
import time

if __name__ == "__main__":
    accel = adxl345.ADXL345()
    
    while(True):
        axis = accel.getAxes()
        sys.stdout.write("\rx:%.3f y:%.3f z:%.3f" % (axis['x'], axis['y'], axis['z']))
	sys.stdout.flush()
        time.sleep(0.02)

