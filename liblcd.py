import RPi.GPIO as GPIO
import time

# LCD						Raspberry Pi
# 1 : GND					-> GND
# 2 : 5V					-> 5V
# 3 : Contrast (0-5V)		-> Variable resistor
# 4 : RS (Register Select)	-> GPIO 7
# 5 : R/W (Read Write)      -> GND
# 6 : Enable or Strobe		-> GPIO 8
# 11: Data Bit 4			-> GPIO 25
# 12: Data Bit 5			-> GPIO 24
# 13: Data Bit 6			-> GPIO 23
# 14: Data Bit 7			-> GPIO 18
# 15: LCD Backlight +5V		-> 5V
# 16: LCD Backlight GND		-> GND


class LCD:
	# Pins mapping
	LCD_RS = 7
	LCD_E  = 8
	LCD_D4 = 25 
	LCD_D5 = 24
	LCD_D6 = 23
	LCD_D7 = 18
	LED_ON = 15

	# Device
	LCD_WIDTH = 16
	LCD_CHR = True
	LCD_CMD = False

	LCD_LINE_1 = 0x80
	LCD_LINE_2 = 0xC0
	#LCD_LINE_3 = 0x94
	#LCD_LINE_4 = 0xD4

	E_PULSE = 0.00005
	E_DELAY = 0.00005

	def init(self):
		try:
			GPIO.setmode(GPIO.BCM)
			GPIO.setup(self.LCD_E, GPIO.OUT)
			GPIO.setup(self.LCD_RS, GPIO.OUT)
			GPIO.setup(self.LCD_D4, GPIO.OUT)
			GPIO.setup(self.LCD_D5, GPIO.OUT)
			GPIO.setup(self.LCD_D6, GPIO.OUT)
			GPIO.setup(self.LCD_D7, GPIO.OUT)
			GPIO.setup(self.LED_ON, GPIO.OUT)
		except: pass

		# Initialise display
		self.byte(0x33,self.LCD_CMD)
		self.byte(0x32,self.LCD_CMD)
		self.byte(0x28,self.LCD_CMD)
		self.byte(0x0C,self.LCD_CMD)  
		self.byte(0x06,self.LCD_CMD)
		self.byte(0x01,self.LCD_CMD)  

	def string(self, message, style):
		# Send string to display
		# style=1 Left justified
		# style=2 Centred
		# style=3 Right justified

		if style==1:
			message = message.ljust(self.LCD_WIDTH," ")  
		elif style==2:
			message = message.center(self.LCD_WIDTH," ")
		elif style==3:
			message = message.rjust(self.LCD_WIDTH," ")

		for i in range(self.LCD_WIDTH):
			self.byte(ord(message[i]),self.LCD_CHR)

	def setline(self, line):
		if line == 1:
			self.byte(self.LCD_LINE_1, self.LCD_CMD)
		elif line == 2:
			self.byte(self.LCD_LINE_2, self.LCD_CMD)

	def byte(self, bits, mode):
		# Send byte to data pins
		# bits = data
		# mode = True  for character
		#        False for command

		GPIO.output(self.LCD_RS, mode) # RS

		# High bits
		GPIO.output(self.LCD_D4, False)
		GPIO.output(self.LCD_D5, False)
		GPIO.output(self.LCD_D6, False)
		GPIO.output(self.LCD_D7, False)
		if bits&0x10==0x10:
			GPIO.output(self.LCD_D4, True)
		if bits&0x20==0x20:
			GPIO.output(self.LCD_D5, True)
		if bits&0x40==0x40:
			GPIO.output(self.LCD_D6, True)
		if bits&0x80==0x80:
			GPIO.output(self.LCD_D7, True)

		# Toggle 'Enable' pin
		time.sleep(self.E_DELAY)    
		GPIO.output(self.LCD_E, True)  
		time.sleep(self.E_PULSE)
		GPIO.output(self.LCD_E, False)  
		time.sleep(self.E_DELAY)      

		# Low bits
		GPIO.output(self.LCD_D4, False)
		GPIO.output(self.LCD_D5, False)
		GPIO.output(self.LCD_D6, False)
		GPIO.output(self.LCD_D7, False)
		if bits&0x01==0x01:
			GPIO.output(self.LCD_D4, True)
		if bits&0x02==0x02:
			GPIO.output(self.LCD_D5, True)
		if bits&0x04==0x04:
			GPIO.output(self.LCD_D6, True)
		if bits&0x08==0x08:
			GPIO.output(self.LCD_D7, True)

		# Toggle 'Enable' pin
		time.sleep(self.E_DELAY)    
		GPIO.output(self.LCD_E, True)  
		time.sleep(self.E_PULSE)
		GPIO.output(self.LCD_E, False)  
		time.sleep(self.E_DELAY)   
