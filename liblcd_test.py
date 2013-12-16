#!/usr/bin/python
import liblcd
import time


def main():
	lcd = liblcd.LCD()
	# Initialise display
	lcd.init()

	# Send some centred test
	lcd.setline(1)
	lcd.string("--------------------",2) 
	lcd.setline(2)
	lcd.string("Rasbperry Pi",2)

	time.sleep(3) # 3 second delay 

	lcd.setline(1)
	lcd.string("COOOOL",3)
	lcd.setline(2)
	lcd.string("paf",3)  

	time.sleep(20) # 20 second delay 

	# Blank display
	lcd.setline(1)
	lcd.string("",3)
	lcd.setline(2)
	lcd.string("",3)


if __name__ == '__main__':
	main()
