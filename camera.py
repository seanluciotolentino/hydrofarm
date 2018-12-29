from driver import camera, stream
from picar import back_wheels, front_wheels
import picar
import time
import requests
from PIL import Image, ImageDraw
from StringIO import StringIO
import os

# set up
picar.setup()
db_file = "/home/pi/SunFounder_PiCar-V/remote_control/remote_control/driver/config"
cam = camera.Camera(debug=False, db=db_file)
cam.ready()
token = os.environ['ifttt_token']
print stream.start()


# keeping track of location
turn_amount = 10
x = y = 0
picture_positions = [('q1', -100, -30), 
					 ('q2', 100, -30), 
					 ('q3', 50, -30), 
					 ('q4',  -50, -30), 
					 ('q5', 0, 50)]

# helper functions for capture
def snap(filename):
	print 'snapping', filename
	url = 'http://192.168.1.194:8080/?action=snapshot'
	filename = '/home/pi/plants/%s.jpg'%filename
	r = requests.get(url)
	i = Image.open(StringIO(r.content))

	# put timestamp on image
	d = ImageDraw.Draw(i)
	timestamp = ' '.join(filename.split('_')[1:])[:-4]
	d.text((10,40),timestamp,(255,255,255))

	i.save(filename)  # save it 

	# send it to the server
	r = requests.post('http://192.168.1.190:5000/record/', files={'file':open(filename, 'rb')})
	print 'pushed to server:', r.status_code
	#os.popen('rm '+filename)

def turn_updown(amt, sleep=1):
	if amt<0:
		cam.turn_down(-amt)
	else:
		cam.turn_up(amt)
	time.sleep(sleep)

def turn_leftright(amt, sleep=1):
	if amt<0:
		cam.turn_left(-amt)
	else:
		cam.turn_right(amt)
	time.sleep(sleep)

def move(leftright, updown):
	turn_leftright(leftright, sleep=0)
	turn_updown(updown, sleep=0)
	time.sleep(1)

def reset():
	x = y = 0
	cam.ready()

def lights(onoff, camgrow):
	cmd = '%s_lights_%s'
	requests.get('https://maker.ifttt.com/trigger/%s/with/key/%s'%(cmd,token))

def capture():
	# turn cam lights on and grow lights off
	lights('on', 'cam')
	lights('off', 'grow')
	time.sleep(2)  # webhooks need a second to process the request

	# iterate over positions 
	timestamp = time.strftime('%Y-%m-%d_%H:%M:%S')
	for quad, x, y in picture_positions:
		move(x, y)
		snap('%s_%s'%(quad,timestamp))
		reset()

	# turn grow lights on and cam lights off
	hour = time.strftime('%H')
	if hour>=23 or <=6:
		lights('on', 'grow')
	lights('off', 'cam')

if __name__ == '__main__':
	try:
		capture()
	except KeyboardInterrupt: 
		pass