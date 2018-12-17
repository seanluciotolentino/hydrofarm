'''
**********************************************************************
* Filename    : views
* Description : views for server
* Author      : Cavon
* Brand       : SunFounder
* E-mail      : service@sunfounder.com
* Website     : www.sunfounder.com
* Update      : Cavon    2016-09-13    New release
**********************************************************************

Modified by Lucio 2018-12-17 to be a standalone script
'''

from driver import camera, stream
from picar import back_wheels, front_wheels
from django.http import HttpResponse
import picar
import time
import requests
from PIL import Image
from StringIO import StringIO
import os

picar.setup()
db_file = "/home/pi/SunFounder_PiCar-V/remote_control/remote_control/driver/config"
fw = front_wheels.Front_Wheels(debug=False, db=db_file)
bw = back_wheels.Back_Wheels(debug=False, db=db_file)
cam = camera.Camera(debug=False, db=db_file)
cam.ready()
bw.ready()
fw.ready()
 
SPEED = 60
bw_status = 0

print stream.start()

def snap(filename):
	print 'snapping', filename
	url = 'http://192.168.1.194:8080/?action=snapshot'
	filename = '/home/pi/plants/%s.jpg'%filename
	r = requests.get(url)
	i = Image.open(StringIO(r.content))
	i.save(filename)  # save it 

	# send it to the server
	r = requests.post('http://192.168.1.190:5000/record/', files={'file':open(filename, 'rb')})
	print 'pushed to server:', r.status_code
	#os.popen('rm '+filename)

def turn_updown(amt):
	if amt<0:
		cam.turn_down(-amt)
	else:
		cam.turn_up(amt)

def run():
	timestamp = time.strftime('%Y-%m-%d_%H:%M:%S')
	for level, amt in [('bottom', -20), ('middle', 10), ('top', 50)]:
		turn_updown(amt)
		cam.turn_left(40)
		time.sleep(1)
		snap('%s_left_%s'%(level,timestamp))
		cam.turn_right(80)  # turn twice the amount to get to the other side
		time.sleep(1)
		snap('%s_right_%s'%(level,timestamp))
		cam.ready()

		# move forward a bit as if on a track
		bw.speed = SPEED
		bw.forward()
		time.sleep(0.1)
		bw.stop()

	# at the end of it all reset
	bw.speed = SPEED
	bw.backward()
	time.sleep(0.1)
	bw.stop()
	bw_status = 0

if __name__ == '__main__':
	try:
		run()
	except KeyboardInterrupt: 
		pass
