from starlette.applications import Starlette
from starlette.templating import Jinja2Templates
from starlette.convertors import register_url_convertor

from .converters import SymbolicConverter, MaterialConverter, SuidConverter
from .display_generator import DisplayGenerator
from .input_sanitizer import InputSanitizer
from .router import SymbolicRouter, MaterialRouter, MiscRouter
from .config import Config

register_url_convertor("symbolic", SymbolicConverter())
register_url_convertor("material", MaterialConverter())
register_url_convertor("suid", SuidConverter())

class Frontend:
    def __init__(self, config_file="frontend.cfg"):
        self.config = Config(config_file)

        self.templates = Jinja2Templates(directory=self.config.templates)

        self.router_kwargs = {
            "templater": self.templates.TemplateResponse,
            "display": DisplayGenerator(),
            "sanitzer": InputSanitizer(),
            "database": self.config.database,
        }

        self.symbolic_router = SymbolicRouter(**self.router_kwargs)
        self.material_router = MaterialRouter(**self.router_kwargs)
        self.misc_router = MiscRouter(static=self.config.static, **self.router_kwargs)

        self.routes = [
            *self.misc_router.routes(),
            *self.symbolic_router.routes(),
            *self.material_router.routes(),
        ]

        self.app = Starlette(debug=self.config.debug, routes=self.routes)
