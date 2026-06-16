from typing import Iterable


def get_register_page(environ, start_response) -> Iterable[bytes]:
    return [b""]


def not_found_page(environ, start_response):
    print("not found")
    pass


def get_request_info(environ, start_response):
    start_response("200 OK", [("Content-Type", "text/html")])
    body = "<br>".join(f"{chave}:{valor}" for chave, valor in environ.items()).encode()
    return [body]
