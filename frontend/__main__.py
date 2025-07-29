from argparse import ArgumentParser

from uvicorn import run

from .app import Frontend

parser = ArgumentParser(prog="SPATS Frontend")
parser.add_argument("-c", "--config")

args = parser.parse_args()

frontend = Frontend(args.config or "frontend.cfg")

app = frontend.app
config = frontend.config

run(app, host=config.host, port=config.port, log_level=config.log_level)