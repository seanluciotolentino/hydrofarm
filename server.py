from flask import Flask, request
app = Flask(__name__)

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
	

if __name__ == '__main__':   
	
	app.run(debug=True)