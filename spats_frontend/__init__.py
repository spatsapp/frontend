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

database = app.config['DATABASE']
display = DisplayGenerator()

@app.before_request
def clear_trailing():
	path = request.path
	if path != '/' and path.endswith('/'):
		return redirect(path[:-1])



@app.route('/', methods=['GET'])
@csrf.exempt
def query_api():
	res = get(f'{database}/').json()
	return render_template('base.html.j2', stuff=f'<pre>{pformat(res)}</pre>')

@app.route('/asset', methods=['GET'])
@csrf.exempt
def asset_all():
	raw = get(f'{database}/asset/all').json()
	res = display.asset_list(raw)
	return render_template('assets.html.j2', objects=res)

@app.route('/asset/<string:_id>', methods=['GET'])
@csrf.exempt
def asset_info(_id):
	raw = get(f'{database}/asset/{_id}').json()
	res = display.asset_info(raw)
	return render_template('asset.html.j2', object=res)

@app.route('/asset/<string:_id>/edit', methods=['GET'])
@csrf.exempt
def asset_edit(_id):
	pass

@app.route('/asset/<string:_id>/new', methods=['GET'])
@csrf.exempt
def asset_new_thing(_id):
	pass

@app.route('/asset/new', methods=['GET'])
@csrf.exempt
def asset_new_type():
	pass


@app.route('/thing', methods=['GET'])
@csrf.exempt
def thing_all():
	raw = get(f'{database}/thing/all').json()
	res = display.thing_list(raw)
	return render_template('list.html.j2', objects=res)

@app.route('/thing/<string:_id>', methods=['GET'])
@csrf.exempt
def thing_info(_id):
	raw = get(f'{database}/thing/{_id}').json()
	res = display.thing_info(raw)
	return render_template('thing.html.j2', object=res)

@app.route('/thing/<string:_id>/edit', methods=['GET'])
@csrf.exempt
def thing_edit():
	pass

@app.route('/thing/asset/<string:_id>', methods=['GET'])
@csrf.exempt
def thing_asset_list(_id):
	raw = get(f'{database}/thing/asset/{_id}').json()
	res = display.thing_list(raw)
	return render_template('list.html.j2', objects=res)


@app.route('/combo', methods=['GET'])
@csrf.exempt
def combo_all():
	pass

@app.route('/combo/<string:_id>', methods=['GET'])
@csrf.exempt
def combo_info(_id):
	pass

@app.route('/combo/<string:_id>/edit', methods=['GET'])
@csrf.exempt
def combo_edit(_id):
	pass

@app.route('/combo/<string:_id>/new', methods=['GET'])
@csrf.exempt
def combo_new_thing(_id):
	pass

@app.route('/combo/new', methods=['GET'])
@csrf.exempt
def combo_new_type():
	pass


@app.route('/group', methods=['GET'])
@csrf.exempt
def group_all():
	pass

@app.route('/group/<string:_id>', methods=['GET'])
@csrf.exempt
def group_info(_id):
	pass

@app.route('/group/<string:_id>/edit', methods=['GET'])
@csrf.exempt
def group_edit(_id):
	pass

@app.route('/group/combo/<string:_id>', methods=['GET'])
@csrf.exempt
def group_combo_list(_id):
	pass


if __name__ == "__main__":
	app.run()