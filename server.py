from flask import Flask, request
from werkzeug.utils import secure_filename
import os
from flask import Flask, render_template
import json

UPLOAD_FOLDER = '/home/lucio/Desktop/hydroimages/'
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route("/")
def index():
	return "Welcome to Hydrofarm Server!"

@app.route('/measure/<string:line>', methods=['GET'])
def measure(line):
	print('measurement=',line)
	try:
		f = open('data/sensor_data.csv', 'a')
		f.write(line.replace('"','')+'\n')
		f.close()
		return 'success', 200
	except Exception as e:
		print("Server can't handle those parameters:", e)
		return 'fail', 400
		
def create_gif(filenames, output_name):
	"""
	helper function to make a gif out of a bunch of filenames
	"""
	print('making gif', output_name)
	images = []
	for filename in sorted(filenames)[-24:]:
		images.append(imageio.imread('%s%s'%(UPLOAD_FOLDER, filename)))
	output_file = './dashboard/static/timelapse/%s.gif'%output_name
	imageio.mimsave(output_file, images, duration=0.5)
	return images


@app.route('/record/', methods=['POST'])
def record():
	"""
	# example usage:
	
	import requests
	fname = 'test.jpg'
	r = requests.post('http://192.168.1.190:5000/record/', files={'file':open(fname, 'rb')})
	"""
	print('record called')
	# check if the post request has the file part
	try:
		if 'file' not in request.files:
			print('no file supplied')
			return 'fail', 400

		# save the file
		file = request.files['file']
		if file and file.filename.endswith('.jpg'):
			filename = secure_filename(file.filename)
			file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

			# if it's the q5 capture - set up the folders for the dashboard
			if 'q5' in file.filename:
				# make a gif of every quadrant
				for q in range(1,6):
					# daily gif
					quad = 'q'+str(q)
					filenames = [f for f in os.listdir(UPLOAD_FOLDER) if quad in f]
					images = create_gif(filenames, quad)
					print(quad, len(images))

				# clear the recents and put the new ones there
				os.popen('rm ./dashboard/static/recent/*').read()  # clear the recent folder 
				all_files = os.listdir(UPLOAD_FOLDER)
				some_files = [sorted([file for file in all_files if 'q'+str(quad) in file]) for quad in range(1,6)]
				for q, quad_files in enumerate(some_files):
					for recent in range(-1, -6, -1):
						os.popen('cp %s%s ../dashboard/static/recent/q%s_%s.jpg'%(UPLOAD_FOLDER, quad_files[recent], q+1, recent*-1)).read()

				# make a file for the time labels too
				times = [quad_files[recent].split('_')[-1][:-4] for recent in range(-1, -6, -1)]
				json.dump(times, open('../dashboard/static/recent/labels.json', 'w'))

			# make weekly gif but only for 7am
			hour = int(file.filename.split('_')[-1].split('/')[0])
			if 'q5' in file.filename and hour==7:
				for q in range(1,6):
					quad = 'q'+str(q)
					filenames = [f for f in os.listdir(UPLOAD_FOLDER) if quad in f]
					images = create_gif(filenames, f'weekly{q}')
					print(quad, len(images))

			return 'sucess', 200

	except Exception as e:
		print("Server can't handle those parameters:", e)
		return 'fail', 400

if __name__ == '__main__':
	app.run(host='0.0.0.0')
