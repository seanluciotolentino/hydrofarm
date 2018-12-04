from flask import Flask, request
from werkzeug.utils import secure_filename
import os

UPLOAD_FOLDER = '/home/lucio/Desktop/hydroimages'
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route("/")
def index():
	return "Welcome to Hydrofarm Server!"

@app.route('/measure/<string:line>', methods=['GET'])
def measure(line):
	print('measurement=',line)
	try:
		f = open('data/sensor_server.csv', 'a')
		f.write(line.replace('"','')+'\n')
		f.close()
		return 'success', 200
	except Exception as e:
		print("Server can't handle those parameters:", e)
		return 'fail', 400
		
@app.route('/record/', methods=['POST'])
def record():
	print('record called')
	# check if the post request has the file part
	try:
	    if 'file' not in request.files:
		    print('no file supplied')
		    return 'fail', 400
	    file = request.files['file']
	    if file and file.filename.endswith('.png'):
		    filename = secure_filename(file.filename)
		    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
		    return 'sucess', 200
	except Exception as e:
		print("Server can't handle those parameters:", e)
		return 'fail', 400

if __name__ == '__main__':
    app.run(host='0.0.0.0')
