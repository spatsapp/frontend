from flask import Flask, request, send_from_directory, render_template, redirect
from flask_wtf.csrf import CSRFProtect
from requests import get, post, put, delete
import dotenv

from pprint import pformat

from .display_generator import DisplayGenerator

app = Flask(__name__, static_url_path='')
app.config.from_pyfile('frontend.cfg')

csrf = CSRFProtect()
csrf.init_app(app)

db = app.config['DATABASE']
dg = DisplayGenerator()

@app.before_request
def clear_trailing():
	path = request.path
	if path != '/' and path.endswith('/'):
		return redirect(path[:-1])

@app.route('/favicon.ico', methods=['GET'])
@csrf.exempt
def favicon():
	return send_from_directory('static', 'favicon.ico', mimetype='image/vnd.microsoft.icon')

@app.route('/', methods=['GET'])
@csrf.exempt
def query_api():
	res = get(f'{db}/').json()
	return res

@app.route('/t/<string:_id>', methods=['GET'])
@csrf.exempt
def thing_get(_id):
	raw = get(f'{db}/thing/{_id}').json()
	res = dg.thing_get(raw)
	return render_template('thing.html.j2', object=res)

@app.route('/a/<string:_id>', methods=['GET'])
@csrf.exempt
def thing_get_all(_id):
	raw = get(f'{db}/thing/asset/{_id}').json()
	res = dg.thing_get_all(raw)
	return render_template('list.html.j2', objects=res)


@app.route('/a', methods=['GET'])
@csrf.exempt
def thing_all():
	raw = get(f'{db}/thing/all').json()
	res = dg.thing_get_all(raw)
	return render_template('list.html.j2', objects=res)


if __name__ == "__main__":
	app.run()