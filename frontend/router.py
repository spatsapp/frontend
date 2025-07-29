from json import load
from http import HTTPStatus

from requests import delete, get, post, put
from starlette.routing import Route, Mount
from starlette.staticfiles import StaticFiles
from starlette.responses import RedirectResponse, JSONResponse


def _symbolic_type(material):
    return "asset" if material == "thing" else "combo"

def _material_type(symbolic):
    return "thing" if symbolic == "asset" else "group"


class GenericRouter:
    def __init__(self, templater, display, sanitzer, database):
        self.templater = templater
        self.display = display
        self.sanitzer = sanitzer
        self.db = database

    def routes(self):
        return []

    def get(self, route, data=None, json=None):
        return get(f"{self.db}/{route}", data=data, json=json).json()

    def put(self, route, data=None, json=None, as_json=False):
        return put(f"{self.db}/{route}", data=data, json=json).json()

    def post(self, route, data=None, json=None, as_json=False):
        return post(f"{self.db}/{route}", data=data, json=json).json()
    
    def delete(self, route, data=None, json=None, as_json=False):
        return delete(f"{self.db}/{route}", data=data, json=json).json()




class SymbolicRouter(GenericRouter):
    def __init__(self, templater, display, sanitzer, database):
        super().__init__(templater=templater, display=display, sanitzer=sanitzer, database=database)


    def routes(self):
        return [
            Mount("/{symbolic:symbolic}", routes=[
                Route("/", self.symbolic_all, methods=["GET"]),
                Route("/new", self.symbolic_new_type_view, methods=["GET"]),
                Route("/new", self.symbolic_new_type_publish, methods=["POST"]),
                Mount("/{_id:suid}", routes=[
                    Route("/", self.symbolic_info, methods=["GET"]),
                    Route("/edit", self.symbolic_edit, methods=["GET"]),
                    Route("/edit", self.symbolic_update, methods=["POST"]),
                    Route("/new", self.symbolic_new_thing_view, methods=["GET"]),
                    Route("/new", self.symbolic_new_thing_publish, methods=["POST"]),
                ]),
            ])
        ]

    def symbolic_all(self, request):
        """Get all assets"""
        symbolic = request.path_params.get("symbolic").value
        raw = self.get(f"/{symbolic}/all")
        res = self.display.symbolic_list(raw)
        return self.templater(
            request,
            "symbolic_list.html.j2",
            context={
                "documents": res,
                "symbolic": symbolic,
                "material": _material_type(symbolic),
            }
        )


    def symbolic_info(self, request):
        """Get specific asset info"""
        symbolic = request.path_params.get("symbolic").value
        _id = request.path_params.get("_id")
        raw = self.get(f"/{symbolic}/{_id}")
        res = self.display.symbolic_info(symbolic, raw)
        return self.templater(
            request,
            "symbolic_info.html.j2",
            context={
                "document": res,
                "symbolic": symbolic,
                "material": _material_type(symbolic),
            }
        )


    def symbolic_edit(self, request):
        """Edit asset"""
        symbolic = request.path_params.get("symbolic").value
        _id = request.path_params.get("_id")
        raw = self.get(f"/{symbolic}/{_id}")
        res = self.display.symbolic_edit(symbolic, raw)
        return self.templater(
            request,
            "symbolic_edit.html.j2",
            context={
                "document": res,
                "symbolic": symbolic,
            }
        )


    async def symbolic_update(self, request):
        """Edit asset"""
        symbolic = request.path_params.get("symbolic").value
        _id = request.path_params.get("_id")
        raw = self.get(f"/{symbolic}/{_id}")
        res = self.display.symbolic_edit(symbolic, raw)
        async with request.form() as form:
            sanitized = self.sanitzer.symbolic_edit(res, form)
        if sanitized:
            update = self.put(f"/{symbolic}/update", json=sanitized)
            if update["errored"]:
                return self.templater(
                    request,
                    "symbolic_edit.html.j2",
                    context={
                        "document": res,
                        "symbolic": symbolic,
                        "error": update["errored"],
                    }
                )
        return RedirectResponse(url=f"/{symbolic}/{_id}", status_code=HTTPStatus.SEE_OTHER)


    def symbolic_new_thing_view(self, request):
        """Create new thing for asset"""
        symbolic = request.path_params.get("symbolic").value
        _id = request.path_params.get("_id")
        material = _material_type(symbolic)
        raw = self.get(f"/{symbolic}/{_id}")
        res = self.display.material_new(symbolic, raw)
        return self.templater(
            request,
            "material_new.html.j2",
            context={
                "document": res,
                "symbolic": symbolic,
                "material": material,
            }
        )


    async def symbolic_new_thing_publish(self, request):
        """Create new thing for asset"""
        symbolic = request.path_params.get("symbolic").value
        _id = request.path_params.get("_id")
        material = _material_type(symbolic)
        raw = self.get(f"/{symbolic}/{_id}")
        res = self.display.material_new(symbolic, raw)

        async with request.form() as form:
            sanitized = self.sanitzer.material_new(res, form)
        new = self.post(f"{material}/create", json=sanitized)
        if new["errored"]:
            return self.templater(
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


    def symbolic_new_type_view(self, request):
        """Create new asset"""
        symbolic = request.path_params.get("symbolic").value
        _id = request.args.get("subtype", f"_{symbolic.title()}")
        raw = self.get(f"/{symbolic}/{_id}")
        res = self.display.symbolic_edit(symbolic, raw)
        return self.templater(
            request,
            "symbolic_new.html.j2",
            context={
                "document": res,
                "symbolic": symbolic,
            }
        )

    async def symbolic_new_type_publish(self, request):
        symbolic = request.path_params.get("symbolic").value

        async with request.form() as form:
            _id = form.get("inherit", f"_{symbolic.title()}")
            raw = self.get(f"/{symbolic}/{_id}")
            res = self.display.symbolic_edit(symbolic, raw)
            sanitized = self.sanitzer.symbolic_new(res, form)
        update = self.post(f"/{symbolic}/create", json=sanitized)
        if update["errored"]:
            return self.templater(
                request,
                "symbolic_new.html.j2",
                context={
                    "document": res,
                    "symbolic": symbolic,
                }
            )
        return RedirectResponse(f"/asset/{update['created'][0]}", status_code=HTTPStatus.SEE_OTHER)



class MaterialRouter(GenericRouter):
    def __init__(self, templater, display, sanitzer, database):
        super().__init__(templater=templater, display=display, sanitzer=sanitzer, database=database)


    def routes(self):
        return [
            Mount("/{material:material}", routes=[
                Route("/", self.material_all_redirect, methods=["GET"]),
                Route("/{page:int}", self.material_all, methods=["GET"]),
                Route("/edit", self.material_edit, methods=["GET"]),
                Route("/edit", self.material_update, methods=["POST"]),
                Mount("/{symbolic:symbolic}/{_id:suid}", routes=[
                    Route("/", self.material_symbolic_list_redirect, methods=["GET"]),
                    Route("/{page:int}", self.material_symbolic_list, methods=["GET"]),
                ]),
                Route("/{_id:suid}", self.material_info, methods=["GET"]),
            ]),
        ]


    def material_all_redirect(self, request):
        """Redirect thing list with no page number to first page"""
        material = request.path_params.get("material").value
        return RedirectResponse(f"/{material}/1", status_code=HTTPStatus.MOVED_PERMANENTLY)


    def material_all(self, request):
        """Get all things"""
        material = request.path_params.get("material").value
        page = request.path_params.get("page")
        symbolic = _symbolic_type(material)
        page = max(page - 1, 0)
        raw = self.get(f"/{material}/all/{page}")
        last = raw.get("paginate", {}).get("last", 1)
        if not raw[symbolic] and last < page:
            return RedirectResponse(f"/{material}/{last}", status_code=HTTPStatus.FOUND)
        res = self.display.material_list(material, symbolic, raw)
        return self.templater(
            request,
            "material_list.html.j2",
            context={
                "documents": res,
                "symbolic": symbolic,
                "material": material,
                "symbolic_id": None,
            }
        )


    def material_info(self, request):
        """Get thing info"""
        material = request.path_params.get("material").value
        _id = request.path_params.get("_id")
        symbolic = _symbolic_type(material)
        raw = self.get(f"/{material}/{_id}")
        res = self.display.material_info(material, symbolic, raw)
        return self.templater(
            request,
            "material_info.html.j2",
            context={
                "document": res,
                "symbolic": symbolic,
                "material": material,
            }
        )


    def material_symbolic_list_redirect(self, request, ):
        material = request.path_params.get("material").value
        symbolic = request.path_params.get("symbolic").value
        _id = request.path_params.get("_id")
        """Redirect thing asset list with no page number to first page"""
        return RedirectResponse(f"/{material}/{symbolic}/{_id}/1", status_code=HTTPStatus.MOVED_PERMANENTLY)



    def material_symbolic_list(self, request):
        """List things for asset"""
        material = request.path_params.get("material").value
        symbolic = request.path_params.get("symbolic").value
        _id = request.path_params.get("_id")
        page = request.path_params.get("page")

        if _symbolic_type(material) != symbolic:
            return RedirectResponse(f"/{material}/{_symbolic_type(material)}/{_id}/{page}", status_code=HTTPStatus.PERMANENT_REDIRECT)

        page = max(page - 1, 0)
        raw = self.get(f"/{material}/{symbolic}/{_id}/{page}")
        last = raw.get("paginate", {}).get("last", 1)
        if not raw[symbolic] and last < page:
            return RedirectResponse(f"/{material}/{symbolic}/{_id}/{last}", status_code=HTTPStatus.FOUND)
        res = self.display.material_list(material, symbolic, raw)
        return self.templater(
            request,
            "material_list.html.j2",
            context={
                "documents": res,
                "symbolic": symbolic,
                "material": material,
                "symbolic_id": _id,
            }
        )


    def material_edit(self, request):
        """Edit thing"""
        material = request.path_params.get("material").value
        _id = request.path_params.get("_id")

        symbolic = _symbolic_type(material)
        raw = self.get(f"/{material}/{_id}")
        res = self.display.material_edit(material, symbolic, raw)
        return self.templater(
            request,
            "material_edit.html.j2",
            context={
                "document": res,
                "symbolic": symbolic,
                "material": material,
            }
        )


    async def material_update(self, request):
        material = request.path_params.get("material").value
        _id = request.path_params.get("_id")
        symbolic = _symbolic_type(material)
        raw = self.get(f"/{material}/{_id}")
        res = self.display.material_edit(material, symbolic, raw)
        async with request.form() as form:
            sanitized = self.sanitzer.material_edit(res, form)
        update = self.put("/thing/update", json=sanitized)
        if update["errored"]:
            return self.templater(
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








class MiscRouter(GenericRouter):
    def __init__(self, templater, display, sanitzer, database, static="static"):
        super().__init__(templater=templater, display=display, sanitzer=sanitzer, database=database)
        self.static = static

    def routes(self):
        return [
            Route("/", self.index, methods=["GET"]),
            Route("/search", self.search, methods=["GET"]),

            Route("/download", self.download, methods=["GET"]),
            Route("/upload", self.upload_view, methods=["GET"]),
            Route("/upload", self.upload_publish, methods=["POST"]),
                
            Mount("/static", StaticFiles(directory=self.static), name="static"),
        ]


    def index(self, request):
        return self.templater(request, "search.html.j2")


    def search(self, request):
        """Search for documents"""
        data = {
            "search": request.query_params.get("search"),
            "collections": request.query_params.get("collection", "").split()
        }
        raw = self.get("/search", json=data)
        res = {"results": self.display.search(raw)}
        return self.templater(request, "search.html.j2", context=res)


    def download(self, _):
        """Downlaod database as a json"""
        res = self.get("/download")
        return JSONResponse(res)


    def upload_view(self, request):
        """Upload json to load info into database"""
        return self.templater(request, "upload.html.j2")


    def upload_publish(self, request):
        filename = request.files["filename"]
        data = load(filename.stream)

        res = self.post("/upload", json=data)
        return JSONResponse(res)

