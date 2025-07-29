# import logging
from os import environ
from typing import Annotated

from dotenv import dotenv_values
from pydantic import BaseModel, DirectoryPath, HttpUrl, AfterValidator, IPvAnyAddress

def level_validator(value: str) -> str:
    if value.lower() not in ["debug", "info", "warning", "error", "critical"]:
        return ValueError(f"{value} is not a valid log level.")
    return value.lower()    

LogLevel = Annotated[str, AfterValidator(level_validator)]


def port_validator(value: str) -> int:
    port = int(value)
    if 0 < port < 65536:
        return port
    raise ValueError("Port is outside of valid range")

Port = Annotated[int, AfterValidator(port_validator)]

class ConfigModel(BaseModel):
    database: HttpUrl | None = "http://localhost:8000"
    templates: DirectoryPath | None = "templates"
    static: DirectoryPath | None = "static"
    debug: bool | None = False
    port: Port | None = 8080
    host: IPvAnyAddress | None = "0.0.0.0"
    workers: int | None = 1
    log_level: LogLevel | None = "info"


class Config:
    def __init__(self, filename="frontend.cfg"):
        dot_config = dotenv_values(filename)
        tmp_config = {
            **({"database": dot} if (dot := dot_config.get("DATABASE")) else {}),
            **({"templates": dot} if (dot := dot_config.get("TEMPLATES")) else {}),
            **({"static": dot} if (dot := dot_config.get("STATIC")) else {}),
            **({"debug": dot} if (dot := dot_config.get("DEBUG")) else {}),
            **({"log_level": dot} if (dot := dot_config.get("LOG_LEVEL")) else {}),
            **self._port(dot_config),
            **self._host(dot_config),
            **self._workers(dot_config)
        }

        self.data = ConfigModel(**tmp_config)

    def _workers(self, config):
        dot = config.get("WORKERS")
        uvicorn = environ.get("WEB_CONCURRENCY")
        if dot or uvicorn:
            return {"workers": dot or uvicorn}
        return {}
    
    def _port(self, config):
        dot = config.get("PORT")
        uvicorn = environ.get("UVICORN_PORT")
        if dot or uvicorn:
            return {"port": dot or uvicorn}
        return {}

    def _host(self, config):
        dot = config.get("HOST")
        uvicorn = environ.get("UVICORN_HOST")
        if dot or uvicorn:
            return {"host": dot or uvicorn}
        return {}

    def __getattr__(self, key):
        return getattr(self.data, key)