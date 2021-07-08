"""Flask frontend for SPATS"""
from pprint import pformat
from json import load

import dotenv
from flask import (
    Flask,
    jsonify,
    redirect,
    render_template,
    request,
    send_from_directory,
)
from flask_wtf.csrf import CSRFProtect
from requests import delete, get, post, put

from .display_generator import DisplayGenerator
from .input_sanitizer import InputSanitizer

app = Flask(__name__, static_url_path="")
app.config.from_pyfile("frontend.cfg")

csrf = CSRFProtect()
csrf.init_app(app)

database = app.config["DATABASE"]
display = DisplayGenerator()
sanitzer = InputSanitizer()


@app.before_request
def clear_trailing():
    """Cleans up requests by removing any trailing slashes"""
    path = request.path
    if path != "/" and path.endswith("/"):
        return redirect(path[:-1])
    return None


@app.route("/", methods=["GET"])
@csrf.exempt
def query_api():
    """Get list of api endpoints"""
    res = get(f"{database}/").json()
    return render_template("base.html.j2", stuff=f"<pre>{pformat(res)}</pre>")


@app.route("/asset", methods=["GET"])
@csrf.exempt
def asset_all():
    """Get all assets"""
    raw = get(f"{database}/asset/all").json()
    res = display.asset_list(raw)
    return render_template(
        "symbolic_list.html.j2",
        documents=res,
        symbolic="asset",
        material="thing",
    )


@app.route("/asset/<string:_id>", methods=["GET"])
@csrf.exempt
def asset_info(_id):
    """Get specific asset info"""
    raw = get(f"{database}/asset/{_id}").json()
    res = display.asset_info(raw)
    return render_template(
        "symbolic_info.html.j2",
        document=res,
        symbolic="asset",
        material="thing",
    )


@app.route("/asset/<string:_id>/edit", methods=["GET", "POST"])
@csrf.exempt
def asset_edit(_id):
    """Edit asset"""
    raw = get(f"{database}/asset/{_id}").json()
    res = display.asset_edit(raw)
    if request.method == "GET":
        return render_template(
            "symbolic_edit.html.j2",
            document=res,
            symbolic="asset",
        )
    sanitized = sanitzer.asset_edit(res, request.form)
    update = put(f"{database}/asset/update", json=sanitized).json()
    if update["errored"]:
        return render_template(
            "symbolic_edit.html.j2",
            document=res,
            symbolic="asset",
            errors=update["errored"],
        )
    return redirect(f"/asset/{_id}")


@app.route("/asset/<string:_id>/new", methods=["GET"])
@csrf.exempt
def asset_new_thing(_id):
    """Create new thing for asset"""


@app.route("/asset/new", methods=["GET"])
@csrf.exempt
def asset_new_type():
    """Create new asset"""


@app.route("/thing", methods=["GET"])
@csrf.exempt
def thing_all():
    """Get all things"""
    raw = get(f"{database}/thing/all").json()
    res = display.thing_list(raw)
    return render_template(
        "material_list.html.j2",
        documents=res,
        symbolic="asset",
        material="thing",
        symbolic_id=None,
    )


@app.route("/thing/<string:_id>", methods=["GET"])
@csrf.exempt
def thing_info(_id):
    """Get thing info"""
    raw = get(f"{database}/thing/{_id}").json()
    res = display.thing_info(raw)
    return render_template(
        "material_info.html.j2",
        document=res,
        symbolic="asset",
        material="thing",
    )


@app.route("/thing/<string:_id>/edit", methods=["GET", "POST"])
@csrf.exempt
def thing_edit(_id):
    """Edit thing"""
    raw = get(f"{database}/thing/{_id}").json()
    res = display.thing_edit(raw)
    if request.method == "GET":
        return render_template(
            "material_edit.html.j2",
            document=res,
            symbolic="asset",
            material="thing",
        )
    sanitized = sanitzer.thing_edit(res, request.form)
    update = put(f"{database}/thing/update", json=sanitized).json()
    if update["errored"]:
        return render_template(
            "material_edit.html.j2",
            document=res,
            symbolic="asset",
            material="thing",
            errors=update["errored"],
        )
    return redirect(f"/thing/{_id}")


@app.route("/thing/asset/<string:_id>", methods=["GET"])
@csrf.exempt
def thing_asset_list(_id):
    """List things for asset"""
    raw = get(f"{database}/thing/asset/{_id}").json()
    res = display.thing_list(raw)
    return render_template(
        "material_list.html.j2",
        documents=res,
        symbolic="asset",
        material="thing",
        symbolic_id=_id,
    )


@app.route("/combo", methods=["GET"])
@csrf.exempt
def combo_all():
    """Get all combos"""
    raw = get(f"{database}/combo/all").json()
    res = display.combo_list(raw)
    return render_template(
        "symbolic_list.html.j2",
        documents=res,
        symbolic="combo",
        material="group",
    )


@app.route("/combo/<string:_id>", methods=["GET"])
@csrf.exempt
def combo_info(_id):
    """Get groups for combo"""
    raw = get(f"{database}/combo/{_id}").json()
    res = display.combo_info(raw)
    return render_template(
        "symbolic_info.html.j2",
        document=res,
        symbolic="combo",
        material="group",
    )


@app.route("/combo/<string:_id>/edit", methods=["GET"])
@csrf.exempt
def combo_edit(_id):
    """Edit combo"""
    raw = get(f"{database}/combo/{_id}").json()
    res = display.combo_edit(raw)
    return render_template(
        "symbolic_edit.html.j2",
        document=res,
        symbolic="combo",
    )


@app.route("/combo/<string:_id>/new", methods=["GET"])
@csrf.exempt
def combo_new_thing(_id):
    """Create group for combo"""


@app.route("/combo/new", methods=["GET"])
@csrf.exempt
def combo_new_type():
    """Create new combo"""


@app.route("/group", methods=["GET"])
@csrf.exempt
def group_all():
    """Get all groups"""
    raw = get(f"{database}/group/all").json()
    res = display.group_list(raw)
    return render_template(
        "material_list.html.j2",
        documents=res,
        symbolic="combo",
        material="group",
        symbolic_id=None,
    )


@app.route("/group/<string:_id>", methods=["GET"])
@csrf.exempt
def group_info(_id):
    """Get info for group"""
    raw = get(f"{database}/group/{_id}").json()
    res = display.group_info(raw)
    return render_template(
        "material_info.html.j2",
        document=res,
        symbolic="combo",
        material="group",
    )


@app.route("/group/<string:_id>/edit", methods=["GET"])
@csrf.exempt
def group_edit(_id):
    """Edit group"""


@app.route("/group/combo/<string:_id>", methods=["GET"])
@csrf.exempt
def group_combo_list(_id):
    """List all groups for combo"""
    raw = get(f"{database}/group/combo/{_id}").json()
    res = display.group_list(raw)
    return render_template(
        "material_list.html.j2",
        documents=res,
        symbolic="combo",
        material="group",
        symbolic_id=_id,
    )

@app.route("/download", methods=["GET"])
@csrf.exempt
def download():
    """Downlaod database as a json"""
    return get(f"{database}/download").json()

@app.route("/upload", methods=["GET","POST"])
@csrf.exempt
def upload():
    """Upload json to load info into database"""
    if request.method == "GET":
        return render_template("upload.html.j2")

    filename = request.files["filename"]
    data = load(filename.stream)
    res = post(f"{database}/upload", json=data)
    return jsonify(res.json())

if __name__ == "__main__":
    app.run()
