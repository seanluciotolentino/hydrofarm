from driver import camera, stream
from picar import back_wheels, front_wheels
import picar
import time
import requests
from PIL import Image, ImageDraw, ImageFont
from StringIO import StringIO
import os

# set up
picar.setup()
db_file = "/home/pi/SunFounder_PiCar-V/remote_control/remote_control/driver/config"
cam = camera.Camera(debug=False, db=db_file)
cam.ready()
token = os.environ['ifttt_token']
print 'stream', stream.start()


# keeping track of location
turn_amount = 10
x = y = 0
picture_positions = [('q1', 90, -50),
					 ('q2', 40, -50),
					 ('q3', 0, -70),
					 ('q4', -50, -50)]

# helper functions for capture
def snap(filename):
	print 'snapping', filename
        url = 'http://192.168.0.160:8080?action=snapshot'
	filename = '/home/pi/plants/%s.jpg'%filename
	r = requests.get(url)
	i = Image.open(StringIO(r.content))

	# put timestamp on image
	d = ImageDraw.Draw(i)
	timestamp = ' '.join(filename.split('_')[1:])[:-4]
	font = ImageFont.truetype("Caladea-Bold.ttf", 35)
	d.text((10,10), timestamp, font=font, fill=(96,244,66))

	i.save(filename)  # save it 

	# send it to the server
	#if 'q4' in filename:  # this is a little hack because the server takes a while to return
	#	lights('cam', 'off')
	r = requests.post('http://96.239.94.115:5000/record/', files={'file':open(filename, 'rb')})
	print 'pushed to server:', r.status_code
	#os.popen('rm '+filename)

def move(leftright, updown):
	if updown<0:
		cam.turn_down(-updown)
	else:
		cam.turn_up(updown)
	if leftright<0:
		cam.turn_left(-leftright)
	else:
		cam.turn_right(leftright)
	time.sleep(5)

def reset():
	x = y = 0
	cam.ready()

def capture():
	# turn cam lights on and grow lights off
	if int(time.strftime('%H'))<6:
		requests.get('https://maker.ifttt.com/trigger/lights_on/with/key/%s'%token)
	time.sleep(5)  # webhooks need a second to process the request

	# iterate over positions 
	timestamp = time.strftime('%Y-%m-%d_%H:%M:%S')
	for quad, x, y in picture_positions:
		move(x, y)
		snap('%s_%s'%(quad,timestamp))
		reset()
		time.sleep(0.1)

	# turn grow lights on and cam lights off
	#hour = int(time.strftime('%H'))
	#if hour>=23 or hour<=6:
	#	lights('grow', 'on')
	#lights('cam', 'off')
	#ssh pi@192.168.0.160
	if int(time.strftime('%H')) < 6:
		requests.get('https://maker.ifttt.com/trigger/lights_off/with/key/%s'%token)

if __name__ == '__main__':
	try:
                stream.start()
		capture()
	except KeyboardInterrupt: 
		pass
