4stability
==========

adxl345
-------

Wiring:

<pre>
pi    adxl
3.3v  3.3v
GND   GND
3.3v  CS
SDA   SDA
SCL   SCL
</pre>

Address I2C: 0x53


servo shield
------------

Wiring:

<pre>
pi    shield
5v    5v
GND   GND
SDA   SDA
SCL   SCL
</pre>

and connection of external power to GND & V+


hc-sr04
-------

Wiring:

<pre>
pi      hc-sr04
5v      Vcc
GND     GND
GPIO23  Trigger
GPIO24  -- 235ohm -- Echo
GPIO24  -- 470ohm -- GND
</pre>


links
-----

+ http://elinux.org/RPi_Low-level_peripherals
+ http://learn.adafruit.com/adafruit-16-channel-servo-driver-with-raspberry-pi/hooking-it-up
