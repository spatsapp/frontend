
from json import load
from enum import Enum
from http import HTTPStatus

from requests import delete, get, post, put
from starlette.applications import Starlette
from starlette.routing import Route, Mount
from starlette.staticfiles import StaticFiles
from starlette.templating import Jinja2Templates
from starlette.convertors import Convertor, register_url_convertor
from starlette.responses import RedirectResponse, JSONResponse

from .display_generator import DisplayGenerator
from .input_sanitizer import InputSanitizer

class Symbolic(str, Enum):
    asset = "asset"
    combo = "combo"

class SymbolicConverter(Convertor):
    regex = f"({'|'.join([v.value for v in Symbolic])})"

    def convert(self, value: str) -> Symbolic:
        return Symbolic[value]

    def to_string(self, value: Symbolic) -> str:
        return str(value)

register_url_convertor("symbolic", SymbolicConverter())


class Material(str, Enum):
    thing = "thing"
    group = "group"

class MaterialConverter(Convertor):
    regex = f"({'|'.join([v.value for v in Material])})"

    def convert(self, value: str) -> Material:
        return Material[value]

    def to_string(self, value: Material) -> str:
        return str(value)

register_url_convertor("material", MaterialConverter())

class SuidConverter(Convertor):
    regex = "[a-z]{7}"

    def convert(self, value: str) -> str:
        return value

    def to_string(self, value: str) -> str:
        return value

register_url_convertor("suid", SuidConverter())


templates = Jinja2Templates(directory="spats_frontend/templates")

database = "http://localhost:8000"
display = DisplayGenerator()
sanitzer = InputSanitizer()


def _symbolic_type(material):
    return "asset" if material == "thing" else "combo"

def _material_type(symbolic):
    return "thing" if symbolic == "asset" else "group"



def index(request):
    return templates.TemplateResponse(request, "search.html.j2")


def search(request):
    """Search for documents"""
    data = {
        "search": request.query_params.get("search"),
        "collections": request.query_params.get("collection", "").split()
    }
    raw = get(f"{database}/search", json=data).json()
    res = {"results": display.search(raw)}
    return templates.TemplateResponse(request, "search.html.j2", context=res)


# @app.route("/<option('asset', 'combo'):symbolic>", methods=["GET"])
def symbolic_all(request):
    """Get all assets"""
    symbolic = request.path_params.get("symbolic").value
    raw = get(f"{database}/{symbolic}/all").json()
    res = display.symbolic_list(raw)
    return templates.TemplateResponse(
        request,
        "symbolic_list.html.j2",
        context={
            "documents": res,
            "symbolic": symbolic,
            "material": _material_type(symbolic),
        }
    )


# @app.route("/<option('asset', 'combo'):symbolic>/<string:_id>", methods=["GET"])
def symbolic_info(request):
    """Get specific asset info"""
    symbolic = request.path_params.get("symbolic").value
    _id = request.path_params.get("_id")
    raw = get(f"{database}/{symbolic}/{_id}").json()
    res = display.symbolic_info(symbolic, raw)
    return templates.TemplateResponse(
        request,
        "symbolic_info.html.j2",
        context={
            "document": res,
            "symbolic": symbolic,
            "material": _material_type(symbolic),
        }
    )


# @app.route("/<option('asset', 'combo'):symbolic>/<string:_id>/edit", methods=["GET"])
def symbolic_edit(request):
    """Edit asset"""
    symbolic = request.path_params.get("symbolic").value
    _id = request.path_params.get("_id")
    raw = get(f"{database}/{symbolic}/{_id}").json()
    res = display.symbolic_edit(symbolic, raw)
    return templates.TemplateResponse(
        request,
        "symbolic_edit.html.j2",
        context={
            "document": res,
            "symbolic": symbolic,
        }
    )


# @app.route("/<option('asset', 'combo'):symbolic>/<string:_id>/edit", methods=["POST"])
async def symbolic_update(request):
    """Edit asset"""
    symbolic = request.path_params.get("symbolic").value
    _id = request.path_params.get("_id")
    raw = get(f"{database}/{symbolic}/{_id}").json()
    res = display.symbolic_edit(symbolic, raw)
    async with request.form() as form:
        sanitized = sanitzer.symbolic_edit(res, form)
    if sanitized:
        update = put(f"{database}/{symbolic}/update", json=sanitized).json()
        if update["errored"]:
            return templates.TemplateResponse(
                request,
                "symbolic_edit.html.j2",
                context={
                    "document": res,
                    "symbolic": symbolic,
                    "error": update["errored"],
                }
            )
    return RedirectResponse(url=f"/{symbolic}/{_id}", status_code=HTTPStatus.SEE_OTHER)


# @app.route("/<option('asset', 'combo'):symbolic>/<string:_id>/new", methods=["GET"])
def symbolic_new_thing_view(request):
    """Create new thing for asset"""
    symbolic = request.path_params.get("symbolic").value
    _id = request.path_params.get("_id")
    material = _material_type(symbolic)
    raw = get(f"{database}/{symbolic}/{_id}").json()
    res = display.material_new(symbolic, raw)
    return templates.TemplateResponse(
        request,
        "material_new.html.j2",
        context={
            "document": res,
            "symbolic": symbolic,
            "material": material,
        }
    )


# @app.route("/<option('asset', 'combo'):symbolic>/<string:_id>/new", methods=["POST"])
async def symbolic_new_thing_publish(request):
    """Create new thing for asset"""
    symbolic = request.path_params.get("symbolic").value
    _id = request.path_params.get("_id")
    material = _material_type(symbolic)
    raw = get(f"{database}/{symbolic}/{_id}").json()
    res = display.material_new(symbolic, raw)

    async with request.form() as form:
        sanitized = sanitzer.material_new(res, form)
    new = post(f"{database}/{material}/create", json=sanitized).json()
    if new["errored"]:
        return templates.TemplateResponse(
            request,
            "material_new.html.j2",
            context={
                "document": res,
                "symbolic": symbolic,
                "material": material,
                "error": new["errored"],
            }
        )
    return RedirectResponse(f"/{material}/{new['created'][0]}", status_code=HTTPStatus.SEE_OTHER)


# @app.route("/<option('asset', 'combo'):symbolic>/new", methods=["GET"])
def symbolic_new_type_view(request):
    """Create new asset"""
    symbolic = request.path_params.get("symbolic").value
    _id = request.args.get("subtype", f"_{symbolic.title()}")
    raw = get(f"{database}/{symbolic}/{_id}").json()
    res = display.symbolic_edit(symbolic, raw)
    return templates.TemplateResponse(
        request,
        "symbolic_new.html.j2",
        context={
            "document": res,
            "symbolic": symbolic,
        }
    )

# @app.route("/<option('asset', 'combo'):symbolic>/new", methods=["POST"])
async def symbolic_new_type_publish(request):
    symbolic = request.path_params.get("symbolic").value

    async with request.form() as form:
        _id = form.get("inherit", f"_{symbolic.title()}")
        raw = get(f"{database}/{symbolic}/{_id}").json()
        res = display.symbolic_edit(symbolic, raw)
        sanitized = sanitzer.symbolic_new(res, form)
    update = post(f"{database}/{symbolic}/create", json=sanitized).json()
    if update["errored"]:
        return templates.TemplateResponse(
            request,
            "symbolic_new.html.j2",
            context={
                "document": res,
                "symbolic": symbolic,
            }
        )
    return RedirectResponse(f"/asset/{update['created'][0]}", status_code=HTTPStatus.SEE_OTHER)


#####

# @app.route("/<option('thing', 'group'):material>", methods=["GET"])
def material_all_redirect(request):
    """Redirect thing list with no page number to first page"""
    material = request.path_params.get("material").value
    return RedirectResponse(f"/{material}/1", status_code=HTTPStatus.MOVED_PERMANENTLY)


# @app.route("/<option('thing', 'group'):material>/page/<int:page>", methods=["GET"])
def material_all(request):
    """Get all things"""
    material = request.path_params.get("material").value
    page = request.path_params.get("page")
    symbolic = _symbolic_type(material)
    page = max(page - 1, 0)
    raw = get(f"{database}/{material}/all/{page}").json()
    last = raw.get("paginate", {}).get("last", 1)
    if not raw[symbolic] and last < page:
        return RedirectResponse(f"/{material}/{last}", status_code=HTTPStatus.FOUND)
    res = display.material_list(material, symbolic, raw)
    return templates.TemplateResponse(
        request,
        "material_list.html.j2",
        context={
            "documents": res,
            "symbolic": symbolic,
            "material": material,
            "symbolic_id": None,
        }
    )


# @app.route("/<option('thing', 'group'):material>/<string:_id>", methods=["GET"])
def material_info(request):
    """Get thing info"""
    material = request.path_params.get("material").value
    _id = request.path_params.get("_id")
    symbolic = _symbolic_type(material)
    raw = get(f"{database}/{material}/{_id}").json()
    res = display.material_info(material, symbolic, raw)
    return templates.TemplateResponse(
        request,
        "material_info.html.j2",
        context={
            "document": res,
            "symbolic": symbolic,
            "material": material,
        }
    )


# @app.route("/<option('thing', 'group'):material>/<option('asset', 'combo'):symbolic>/<string:_id>", methods=["GET"])
def material_symbolic_list_redirect(request, ):
    material = request.path_params.get("material").value
    symbolic = request.path_params.get("symbolic").value
    _id = request.path_params.get("_id")
    """Redirect thing asset list with no page number to first page"""
    return RedirectResponse(f"/{material}/{symbolic}/{_id}/1", status_code=HTTPStatus.MOVED_PERMANENTLY)



# @app.route("/<option('thing', 'group'):material>/<option('asset', 'combo'):symbolic>/<string:_id>/<int:page>", methods=["GET"])
def material_symbolic_list(request):
    """List things for asset"""
    material = request.path_params.get("material").value
    symbolic = request.path_params.get("symbolic").value
    _id = request.path_params.get("_id")
    page = request.path_params.get("page")

    if _symbolic_type(material) != symbolic:
        return RedirectResponse(f"/{material}/{_symbolic_type(material)}/{_id}/{page}", status_code=HTTPStatus.PERMANENT_REDIRECT)

    page = max(page - 1, 0)
    raw = get(f"{database}/{material}/{symbolic}/{_id}/{page}").json()
    last = raw.get("paginate", {}).get("last", 1)
    if not raw[symbolic] and last < page:
        return RedirectResponse(f"/{material}/{symbolic}/{_id}/{last}", status_code=HTTPStatus.FOUND)
    res = display.material_list(material, symbolic, raw)
    return templates.TemplateResponse(
        request,
        "material_list.html.j2",
        context={
            "documents": res,
            "symbolic": symbolic,
            "material": material,
            "symbolic_id": _id,
        }
    )


# @app.route("/thing/<string:_id>/edit", methods=["GET"])
def material_edit(request):
    """Edit thing"""
    material = request.path_params.get("material").value
    _id = request.path_params.get("_id")

    symbolic = _symbolic_type(material)
    raw = get(f"{database}/{material}/{_id}").json()
    res = display.material_edit(material, symbolic, raw)
    return templates.TemplateResponse(
        request,
        "material_edit.html.j2",
        context={
            "document": res,
            "symbolic": symbolic,
            "material": material,
        }
    )


# @app.route("/thing/<string:_id>/edit", methods=[ "POST"])
async def material_update(request):
    material = request.path_params.get("material").value
    _id = request.path_params.get("_id")
    symbolic = _symbolic_type(material)
    raw = get(f"{database}/{material}/{_id}").json()
    res = display.material_edit(material, symbolic, raw)
    async with request.form() as form:
        sanitized = sanitzer.material_edit(res, form)
    update = put(f"{database}/thing/update", json=sanitized).json()
    if update["errored"]:
        return templates.TemplateResponse(
            request,
            "material_edit.html.j2",
            context={
                "document": res,
                "symbolic": symbolic,
                "material": material,
                "error": update["errored"],
            }
        )
    return RedirectResponse(f"/{material}/{_id}", status_code=HTTPStatus.SEE_OTHER)



# @app.route("/download", methods=["GET"])
def download(_):
    """Downlaod database as a json"""
    return get(f"{database}/download").json()


# @app.route("/upload", methods=["GET"])
def upload_view(request):
    """Upload json to load info into database"""
    return templates.TemplateResponse(request, "upload.html.j2")

# @app.route("/upload", methods=["POST"])
def upload_publish(request):
    filename = request.files["filename"]
    data = load(filename.stream)

    res = post(f"{database}/upload", json=data)
    return JSONResponse(res.json())





routes = [
    Route("/", index, methods=["GET"]),
    Route("/search", search, methods=["GET"]),

    Mount("/{symbolic:symbolic}", routes=[
        Route("/", symbolic_all, methods=["GET"]),
        Route("/new", symbolic_new_type_view, methods=["GET"]),
        Route("/new", symbolic_new_type_publish, methods=["POST"]),
        Mount("/{_id:suid}", routes=[
            Route("/", symbolic_info, methods=["GET"]),
            Route("/edit", symbolic_edit, methods=["GET"]),
            Route("/edit", symbolic_update, methods=["POST"]),
            Route("/new", symbolic_new_thing_view, methods=["GET"]),
            Route("/new", symbolic_new_thing_publish, methods=["POST"]),
        ]),
    ]),

    Mount("/{material:material}", routes=[
        Route("/", material_all_redirect, methods=["GET"]),
        Route("/{page:int}", material_all, methods=["GET"]),
        Route("/edit", material_edit, methods=["GET"]),
        Route("/edit", material_update, methods=["POST"]),
        Mount("/{symbolic:symbolic}/{_id:suid}", routes=[
            Route("/", material_symbolic_list_redirect, methods=["GET"]),
            Route("/{page:int}", material_symbolic_list, methods=["GET"]),
        ]),
        Route("/{_id:suid}", material_info, methods=["GET"]),
    ]),

    Route("/download", download, methods=["GET"]),
    Route("/upload", upload_view, methods=["GET"]),
    Route("/upload", upload_publish, methods=["POST"]),
        
    Mount("/static", StaticFiles(directory="spats_frontend/static"), name="static")
]

app = Starlette(debug=True, routes=routes)
