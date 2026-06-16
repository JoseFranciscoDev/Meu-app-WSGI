from typing import Iterable
from wsgiref.simple_server import make_server
from rotas import rotas
from controllers import not_found_page
from wsgi_types import WSGIDict

endereco = ("0.0.0.0", 3333)
host, port = endereco


def app(environ: WSGIDict, start_response) -> Iterable[bytes]:
    rota = environ["PATH_INFO"]
    handler = rotas.get(rota, not_found_page)
    return handler(environ, start_response)


server = make_server(host, port, app)
server.serve_forever()
