from flask import Flask, request
from werkzeug.utils import secure_filename
import os

#UPLOAD_FOLDER = '/home/lucio/Desktop/hydroimages'
UPLOAD_FOLDER = '/Users/stolentino/Desktop/hydroimages'
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route("/")
def index():
	return "Welcome to Hydrofarm Server!"

@app.route('/measure/', methods=['GET'])
def measure():
	# show the post with the given id, the id is an integer
	print('measurement received:', request.args.to_dict())
	try:
		line = '{ts},{temp},{light},{moisture}'.format(**request.args.to_dict())
		f = open('data/junk.csv', 'a')
		f.write(line+'\n')
		f.close()
		return 'success', 200
	except Exception:
		print("Server can't handle those parameters")
		return 'fail', 400
	
@app.route('/record/', methods=['POST'])
def record():
	print('record called')
	# check if the post request has the file part
	if 'file' not in request.files:
		print('no file supplied')
		return 'fail', 400
	file = request.files['file']
	if file and file.filename.endswith('.png'):
		filename = secure_filename(file.filename)
		file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
		return 'sucess', 200

if __name__ == '__main__':   
	app.run(debug=True)