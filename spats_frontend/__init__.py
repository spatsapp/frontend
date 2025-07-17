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
    url_for,
)

# from flask_wtf.csrf import CSRFProtect
from requests import delete, get, post, put
from werkzeug.routing import BaseConverter, ValidationError

from .display_generator import DisplayGenerator
from .input_sanitizer import InputSanitizer


class OptionConverter(BaseConverter):
    """URL converter that only allows things in the list"""

    def __init__(self, url_map, *args):
        super().__init__(url_map)
        self.options = set(args)

    def to_python(self, value):
        if value not in self.options:
            raise ValidationError()
        return value

    def to_url(self, value):
        return value


app = Flask(__name__, static_url_path="/static")
app.config.from_pyfile("frontend.cfg")
app.url_map.converters["option"] = OptionConverter


# csrf = CSRFProtect()
# csrf.init_app(app)

database = app.config["DATABASE"]
display = DisplayGenerator()
sanitzer = InputSanitizer()


def _symbolic_type(material):
    return "asset" if material == "thing" else "combo"


def _material_type(symbolic):
    return "thing" if symbolic == "asset" else "group"


@app.before_request
def clear_trailing():
    """Cleans up requests by removing any trailing slashes"""
    path = request.path
    if path != "/" and path.endswith("/"):
        return redirect(path[:-1])
    return None


@app.route("/", methods=["GET"])
def index():
    """Get list of api endpoints"""
    return render_template("search.html.j2")

@app.route("/search", methods=["GET"])
def search():
    """Search for documents"""
    raw = post(f"{database}/search", json=request.args).json()
    res = display.search(raw)
    return render_template(
        "search.html.j2",
        results=res,
    )

@app.route("/<option('asset', 'combo'):symbolic>", methods=["GET"])
def symbolic_all(symbolic):
    """Get all assets"""
    raw = get(f"{database}/{symbolic}/all").json()
    res = display.symbolic_list(raw)
    return render_template(
        "symbolic_list.html.j2",
        documents=res,
        symbolic=symbolic,
        material=_material_type(symbolic),
    )


@app.route("/<option('asset', 'combo'):symbolic>/<string:_id>", methods=["GET"])
def symbolic_info(symbolic, _id):
    """Get specific asset info"""
    raw = get(f"{database}/{symbolic}/{_id}").json()
    res = display.symbolic_info(symbolic, raw)
    return render_template(
        "symbolic_info.html.j2",
        document=res,
        symbolic=symbolic,
        material=_material_type(symbolic),
    )


@app.route(
    "/<option('asset', 'combo'):symbolic>/<string:_id>/edit",
    methods=["GET", "POST"],
)
def symbolic_edit(symbolic, _id):
    """Edit asset"""
    raw = get(f"{database}/{symbolic}/{_id}").json()
    res = display.symbolic_edit(symbolic, raw)
    if request.method == "GET":
        return render_template(
            "symbolic_edit.html.j2",
            document=res,
            symbolic=symbolic,
        )
    sanitized = sanitzer.symbolic_edit(res, request.form)
    update = put(f"{database}/{symbolic}/update", json=sanitized).json()
    if update["errored"]:
        return render_template(
            "symbolic_edit.html.j2",
            document=res,
            symbolic=symbolic,
            error=update["errored"],
        )
    return redirect(f"/{symbolic}/{_id}")


@app.route(
    "/<option('asset', 'combo'):symbolic>/<string:_id>/new",
    methods=["GET", "POST"],
)
def symbolic_new_thing(symbolic, _id):
    """Create new thing for asset"""
    material = _material_type(symbolic)
    raw = get(f"{database}/{symbolic}/{_id}").json()
    res = display.material_new(symbolic, raw)
    if request.method == "GET":
        return render_template(
            "material_new.html.j2",
            document=res,
            symbolic=symbolic,
            material=material,
        )
    sanitized = sanitzer.material_new(res, request.form)
    new = post(f"{database}/{material}/create", json=sanitized).json()
    if new["errored"]:
        return render_template(
            "material_new.html.j2",
            document=res,
            symbolic=symbolic,
            material=material,
            error=new["errored"],
        )
    return redirect(f"/{material}/{new['created'][0]}")


@app.route("/<option('asset', 'combo'):symbolic>/new", methods=["GET", "POST"])
def symbolic_new_type(symbolic):
    """Create new asset"""
    if request.method == "GET":
        _id = request.args.get("subtype", f"_{symbolic.title()}")
        raw = get(f"{database}/{symbolic}/{_id}").json()
        res = display.symbolic_edit(symbolic, raw)
        return render_template(
            "symbolic_new.html.j2",
            document=res,
            symbolic=symbolic,
        )
    _id = request.form.get("inherit", f"_{symbolic.title()}")
    raw = get(f"{database}/{symbolic}/{_id}").json()
    res = display.symbolic_edit(symbolic, raw)
    sanitized = sanitzer.symbolic_new(res, request.form)
    update = post(f"{database}/{symbolic}/create", json=sanitized).json()
    if update["errored"]:
        return render_template(
            "symbolic_new.html.j2",
            document=res,
            symbolic=symbolic,
        )
    return redirect(f"/asset/{update['created'][0]}")


# @app.route("/<option('thing', 'group'):material>", methods=["GET"])
# def material_all_redirect(material):
#     """Redirect thing list with no page number to first page"""
#     return redirect(f"/{material}/page/1")


@app.route("/<option('thing', 'group'):material>/page/<int:page>", methods=["GET"])
def material_all(material, page):
    """Get all things"""
    symbolic = _symbolic_type(material)
    page = max(page - 1, 0)
    raw = get(f"{database}/{material}/all/{page}").json()
    last = raw.get("paginate", {}).get("last", 1)
    if not raw[symbolic] and last < page:
        return redirect(f"/{material}/{last}")
    res = display.material_list(material, symbolic, raw)
    return render_template(
        "material_list.html.j2",
        documents=res,
        symbolic=symbolic,
        material=material,
        symbolic_id=None,
    )



# @app.route("/<option('thing', 'group'):material>/<string:_id>", methods=["GET"])
@app.route("/thing/<string:_id>", methods=["GET"])
def material_info(_id):
    """Get thing info"""
    symbolic = _symbolic_type("thing")
    raw = get(f"{database}/thing/{_id}").json()
    res = display.material_info("thing", symbolic, raw)
    return render_template(
        "material_info.html.j2",
        document=res,
        symbolic=symbolic,
        material="thing",
    )


# @app.route(
#     "/<option('thing', 'group'):material>/<option('asset', 'combo'):symbolic>/<string:_id>",
#     methods=["GET"],
# )
# def material_symbolic_list_redirect(material, symbolic, _id):
#     """Redirect thing asset list with no page number to first page"""
#     return redirect(f"/{material}/{symbolic}/{_id}/1")


# @app.route(
#     (
#         "/<option('thing', 'group'):material>"
#         "/<option('asset', 'combo'):symbolic>"
#         "/<string:_id>"
#         "/<int:page>"
#     ),
#     methods=["GET"],
# )
# def material_symbolic_list(material, symbolic, _id, page):
#     """List things for asset"""
#     if _symbolic_type(material) != symbolic:
#         return redirect(f"/{material}/{_symbolic_type(material)}/{_id}/{page}")
#     page = max(page - 1, 0)
#     raw = get(f"{database}/{material}/{symbolic}/{_id}/{page}").json()
#     last = raw.get("paginate", {}).get("last", 1)
#     if not raw[symbolic] and last < page:
#         return redirect(f"/{material}/{symbolic}/{_id}/{last}")
#     res = display.material_list(material, symbolic, raw)
#     return render_template(
#         "material_list.html.j2",
#         documents=res,
#         symbolic=symbolic,
#         material=material,
#         symbolic_id=_id,
#     )


@app.route(
    "/thing/<string:_id>/edit",
    methods=["GET", "POST"],
)
def material_edit(_id):
    """Edit thing"""
    symbolic = _symbolic_type("thing")
    raw = get(f"{database}/thing/{_id}").json()
    res = display.material_edit("thing", symbolic, raw)
    if request.method == "GET":
        return render_template(
            "material_edit.html.j2",
            document=res,
            symbolic=symbolic,
            material="thing",
        )
    sanitized = sanitzer.material_edit(res, request.form)
    update = put(f"{database}/thing/update", json=sanitized).json()
    if update["errored"]:
        return render_template(
            "material_edit.html.j2",
            document=res,
            symbolic=symbolic,
            material="thing",
            error=update["errored"],
        )
    return redirect(f"/thing/{_id}")


@app.route("/download", methods=["GET"])
def download():
    """Downlaod database as a json"""
    return get(f"{database}/download").json()


@app.route("/upload", methods=["GET", "POST"])
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
