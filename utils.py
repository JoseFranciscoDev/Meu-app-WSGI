from urllib.parse import parse_qs
import os
from jinja2 import Environment, FileSystemLoader
from typing import Iterable


jinja_env = Environment(
    loader=FileSystemLoader(os.path.join(os.path.dirname(os.path.abspath(__file__)), "templates"))
)


def _render(template_name: str, **ctx) -> bytes:
    return jinja_env.get_template(template_name).render(**ctx).encode()


def _html(
    start_response, status: str, body: bytes, extra_headers: list | None = None
) -> Iterable[bytes]:
    headers = [
        ("Content-Type", "text/html; charset=utf-8"),
        ("Content-Length", str(len(body))),
    ]
    if extra_headers:
        headers.extend(extra_headers)
    start_response(status, headers)
    return [body]


def _read_post_body(environ) -> dict[str, list[str]]:
    length = int(environ.get("CONTENT_LENGTH") or 0)
    if length <= 0:
        return {}
    return parse_qs(environ["wsgi.input"].read(length).decode("utf-8"))


def _first(form: dict, key: str) -> str:
    return form.get(key, [""])[0]
