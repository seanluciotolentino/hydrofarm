#!/usr/bin/env python
import PCF8591 as ADC
import math
import sys

TEMP_PIN = 0
LIGHT_PIN = 2
MOISTURE_PIN = 1
SLEEP_LENGTH = 5*60  # 5 minutes?

def get_temperature():
	# there's math on top of the analog read so make it a function
	analogVal = ADC.read(TEMP_PIN)
	Vr = 5 * float(analogVal) / 255
	Rt = 10000 * Vr / (5 - Vr)
	temp = 1/(((math.log(Rt / 10000)) / 3950) + (1 / (273.15+25)))
	return temp - 273.15


def run():
	# collect the data
	temp = get_temperature()  # there's some math with this
	light = ADC.read(LIGHT_PIN)
	moisture = ADC.read(MOISTURE_PIN)
	timestamp = time.strftime('%Y-%m-%d %H:%M:%S')

	# write the data
	print ','.join([str(v) for v in [timestamp,temp, light, moisture]])
	sys.stdout.flush()

if __name__ == '__main__':
	try:
		ADC.setup(0x48)  # I'm not sure exactly what this does but seems necessary
		run()
	except KeyboardInterrupt: 
		pass
