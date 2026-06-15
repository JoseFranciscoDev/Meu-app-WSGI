from wsgiref.simple_server import make_server

endereco = ("0.0.0.0", 3333)
host, port = endereco


def app(environ, start_response):
    if environ["PATH_INFO"] == "/request/info":
        start_response("200 OK", [("Content-Type", "text/html")])
        body = "<br>".join(
            f"{chave}:{valor}" for chave, valor in environ.items()
        ).encode()
        return [body]
    start_response("404 Not Found", [("Content-Type", "text/plain")])
    return [b"Not Found"]


server = make_server(host, port, app)
server.serve_forever()
