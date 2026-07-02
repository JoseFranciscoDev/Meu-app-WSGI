from typing import Iterable
from wsgiref.simple_server import make_server
from wsgiref.types import StartResponse, WSGIEnvironment
import sys
from controllers import not_found_page, router


arguments = sys.argv

if len(arguments) > 3:
    raise Exception("Você só pode passar dois argumentos: host porta")
if len(arguments) < 3:
    raise Exception("Você deve passar dois argumentos: host porta")

port = int(arguments[2])
host = arguments[1]


def app(environ: WSGIEnvironment, start_response: StartResponse) -> Iterable[bytes]:
    
    method = environ["REQUEST_METHOD"]
    path = environ["PATH_INFO"]
    handler = router.routes.get((method, path), not_found_page)
    return handler(environ, start_response)


server = make_server(host, port, app)
server.serve_forever()
