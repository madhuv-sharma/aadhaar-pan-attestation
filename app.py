from flask import Flask, request
# from flask_ngrok import run_with_ngrok
# from io import BytesIO
from PIL import Image, ImageChops
import base64
import cv2
import json
import pathlib
import urllib.request


app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False
# run_with_ngrok(app)


def error_handle(error_message, code=1, status=500, mimetype='application/json'):
	return Response(json.dumps({"success" : False, "message": error_message, "data": { "modelname": "" }, "code": code }), status=status, mimetype=mimetype)


def fix(image, x, y):
	dimensions = image.shape
	if dimensions[0] < y or dimensions[1] < x :
		return error_handle("Input Image should be of minimum dimensions {}*{}!".format(x, y))
	image = auto_fix(image)
	return cv2.resize(image, (x, y), interpolation = cv2.INTER_AREA)


def auto_fix(image, clip_hist_percent=1):
	gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
	hist = cv2.calcHist([gray],[0],None,[256],[0,256])
	hist_size = len(hist)
	accumulator = []
	accumulator.append(float(hist[0]))
	for index in range(1, hist_size):
		accumulator.append(accumulator[index -1] + float(hist[index]))
	maximum = accumulator[-1]
	clip_hist_percent *= (maximum/100.0)
	clip_hist_percent /= 2.0
	minimum_gray = 0
	while accumulator[minimum_gray] < clip_hist_percent:
		minimum_gray += 1
	maximum_gray = hist_size -1
	while accumulator[maximum_gray] >= (maximum - clip_hist_percent):
		maximum_gray -= 1
	alpha = 255 / (maximum_gray - minimum_gray)
	beta = -minimum_gray * alpha
	auto_result = cv2.convertScaleAbs(image, alpha=alpha, beta=beta)
	return auto_result


'''
def im_2_b64(image):
	buff = BytesIO()
	image.save(buff, format="JPEG")
	img_str = base64.b64encode(buff.getvalue())
	return img_str
'''


@app.route('/')
def welcome():
	return 'Welcome!'


@app.route('/index')
def index():
	return '''
	/api/aadhaar for Aadhaar Card Attestation
	/api/pan for PAN Card Attestation
	'''

# Aadhaar Card Attestation
@app.route('/api/aadhaar', methods=['POST', 'GET'])
def aadhaar(xa = 660, ya = 420, xs = 250, ys = 80):
	if request.method == 'POST':
		if ('url1' not in request.form) or ('url2' not in request.form) or ('url3' not in request.form):
			return error_handle('Please send all 3 image URLs!')

		url1 = request.form.get('url1')
		file_extension = pathlib.Path(url1).suffix
		f1 = "AadhaarF{}".format(file_extension)
		urllib.request.urlretrieve(url1, f1)
		aad_f = cv2.imread(f1)
		aad_f = fix(aad_f, xa, ya)
		temp = cv2.cvtColor(aad_f, cv2.COLOR_BGR2RGB)
		aad_f_pil = Image.fromarray(temp)

		url2 = request.form.get('url2')
		file_extension = pathlib.Path(url2).suffix
		f2 = "AadhaarB{}".format(file_extension)
		urllib.request.urlretrieve(url2, f2)
		aad_b = cv2.imread(f2)
		aad_b = fix(aad_b, xa, ya)
		temp = cv2.cvtColor(aad_b, cv2.COLOR_BGR2RGB)
		aad_b_pil = Image.fromarray(temp)

		url3 = request.form.get('url3')
		file_extension = pathlib.Path(url3).suffix
		f3 = "Sign{}".format(file_extension)
		urllib.request.urlretrieve(url3, f3)
		sig = cv2.imread(f3)
		sig = fix(sig, xs, ys)
		temp = cv2.cvtColor(sig, cv2.COLOR_BGR2RGB)
		sig_pil = Image.fromarray(temp)

		w = xa
		h = 2*ya + ys
		out = Image.new("RGBA", (w, h), (255, 255, 255, 255))
		out.paste(aad_f_pil, box=(0,0,w,ya))
		out.paste(aad_b_pil, box=(0,ya,w,2*ya))
		out.paste(sig_pil, box=(0,2*ya,xs,h))
		# return im_2_b64(out)
		return base64.b64encode(out.tobytes())
	return '''
		<!DOCTYPE HTML>
		<title>Aadhaar Card Attestation</title>
		<h1>Upload 3 URLs</h1>
		<form method=post enctype=multipart/form-data>
		<input type=text name=url1>
		<input type=text name=url2>
		<input type=text name=url3>
		<input type=submit value=Upload>
		</form>
		'''


# PAN Card Attestation
@app.route('/api/pan', methods=['POST','GET'])
def pan(xp = 700, yp = 500, xs = 250, ys = 80):
	if request.method == 'POST':
		if ('url1' not in request.form) or ('url2' not in request.form):
				return error_handle('Please send both image URLs!')

		url1 = request.form.get('url1')
		file_extension = pathlib.Path(url1).suffix
		f1 = "PAN{}".format(file_extension)
		urllib.request.urlretrieve(url1, f1)
		p = cv2.imread(f1)
		p = fix(p, xp, yp)
		temp = cv2.cvtColor(p, cv2.COLOR_BGR2RGB)
		p_pil = Image.fromarray(temp)

		url2 = request.form.get('url2')
		file_extension = pathlib.Path(url2).suffix
		f2 = "Sign{}".format(file_extension)
		urllib.request.urlretrieve(url2, f2)
		sig = cv2.imread(f2)
		sig = fix(sig, xs, ys)
		temp = cv2.cvtColor(sig, cv2.COLOR_BGR2RGB)
		sig_pil = Image.fromarray(temp)

		w = xp
		h = yp + ys
		out = Image.new("RGBA", (w, h), (255, 255, 255, 255))
		out.paste(p_pil, box=(0,0,w,yp))
		out.paste(sig_pil, box=(0,yp,xs,h))
		# return im_2_b64(out)
		return base64.b64encode(out.tobytes())
	return '''
		<!DOCTYPE HTML>
		<title>PAN Card Attestation</title>
		<h1>Upload 2 URLs</h1>
		<form method=post enctype=multipart/form-data>
		<input type=text name=url1>
		<input type=text name=url2>
		<input type=submit value=Upload>
		</form>
		'''


app.run()