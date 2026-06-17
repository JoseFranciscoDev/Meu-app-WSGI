from typing import Iterable
from wsgiref.simple_server import make_server
from wsgiref.types import StartResponse, WSGIEnvironment

from controllers import not_found_page
from rotas import rotas


def app(environ: WSGIEnvironment, start_response: StartResponse) -> Iterable[bytes]:
    method = environ["REQUEST_METHOD"]
    path = environ["PATH_INFO"]
    handler = rotas.get((method, path), not_found_page)
    return handler(environ, start_response)


server = make_server("0.0.0.0", 8080, app)
server.serve_forever()
