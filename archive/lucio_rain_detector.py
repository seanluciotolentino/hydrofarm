#!/usr/bin/env python
import PCF8591 as ADC
import RPi.GPIO as GPIO
import time
import math
import sys
#sys.stdout = open('data/sensor_data.csv', 'w')


DO = 17
GPIO.setmode(GPIO.BCM)

def setup():
	ADC.setup(0x48)
	GPIO.setup(DO, GPIO.IN)

def Print(x):
	if x == 1:
		print ''
		print '   ***************'
		print '   * Not raining *'
		print '   ***************'
		print ''
	if x == 0:
		print ''
		print '   *************'
		print '   * Raining!! *'
		print '   *************'
		print ''

def loop():
	while True:
            print time.strftime('%Y-%m-%d %H:%M:%S'),',',ADC.read(0)
            sys.stdout.flush()
            time.sleep(30)

if __name__ == '__main__':
	try:
		setup()
		loop()
	except KeyboardInterrupt: 
		pass	
