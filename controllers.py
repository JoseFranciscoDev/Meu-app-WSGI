import os
from urllib.parse import parse_qs

from jinja2 import Environment, FileSystemLoader

import auth
import database
import sessions

_jinja_env = Environment(
    loader=FileSystemLoader(
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "templates")
    )
)


def _render(template_name: str, **ctx) -> bytes:
    return _jinja_env.get_template(template_name).render(**ctx).encode()


def _html(start_response, status: str, body: bytes, extra_headers: list | None = None) -> list:
    headers = [
        ("Content-Type", "text/html; charset=utf-8"),
        ("Content-Length", str(len(body))),
    ]
    if extra_headers:
        headers.extend(extra_headers)
    start_response(status, headers)
    return [body]


def _read_post_body(environ) -> dict[str, list[str]]:
    try:
        length = int(environ.get("CONTENT_LENGTH") or 0)
    except ValueError:
        length = 0
    if length <= 0:
        return {}
    return parse_qs(environ["wsgi.input"].read(length).decode("utf-8"))


def _first(form: dict, key: str) -> str:
    return form.get(key, [""])[0]


def unauthorized_page(environ, start_response):
    body = _render("unauthorized.html", user_email=None)
    return _html(start_response, "401 Unauthorized", body)


def not_found_page(environ, start_response):
    body = _render("not_found.html", user_email=None)
    return _html(start_response, "404 Not Found", body)


def get_home_page(environ, start_response):
    email = sessions.get_authenticated_email(environ)
    body = _render("home.html", user_email=email)
    return _html(start_response, "200 OK", body)


def get_register_page(environ, start_response):
    body = _render("register.html", user_email=None)
    return _html(start_response, "200 OK", body)


def post_register(environ, start_response):
    form = _read_post_body(environ)
    email = _first(form, "email")
    password = _first(form, "password")

    if email in database.users:
        body = _render("register_conflict.html", user_email=None)
        return _html(start_response, "409 Conflict", body)

    salt = auth.generate_salt()
    password_hash = auth.hash_password(password, salt)
    database.users[email] = {"salt": salt, "password_hash": password_hash}

    body = _render("register_success.html", user_email=None)
    return _html(start_response, "200 OK", body)


def get_login_page(environ, start_response):
    body = _render("login.html", user_email=None)
    return _html(start_response, "200 OK", body)


def post_login(environ, start_response):
    form = _read_post_body(environ)
    email = _first(form, "email")
    password = _first(form, "password")

    user = database.users.get(email)
    if user is None or not auth.verify_password(password, user["salt"], user["password_hash"]):
        body = _render("login_error.html", user_email=None)
        return _html(start_response, "401 Unauthorized", body)

    session_id = sessions.create_session(email)
    cookie = f"sessionId={session_id}; HttpOnly; Path=/; SameSite=Strict"
    start_response("302 Found", [
        ("Location", "/dashboard"),
        ("Set-Cookie", cookie),
        ("Content-Length", "0"),
    ])
    return [b""]


def get_dashboard(environ, start_response):
    email = sessions.get_authenticated_email(environ)
    if email is None:
        return unauthorized_page(environ, start_response)
    body = _render("dashboard.html", user_email=email)
    return _html(start_response, "200 OK", body)


def get_admin(environ, start_response):
    email = sessions.get_authenticated_email(environ)
    if email is None:
        return unauthorized_page(environ, start_response)

    user_list = [
        {
            "email": u_email,
            "salt": data["salt"],
            "hash_preview": data["password_hash"][:32],
        }
        for u_email, data in database.users.items()
    ]

    session_list = [
        {
            "session_id": sid,
            "email": data["email"],
            "created_at": data["created_at"].strftime("%d/%m/%Y"),
            "views": data["views"],
        }
        for sid, data in database.sessions.items()
    ]

    body = _render("admin.html", user_email=email, users=user_list, sessions=session_list)
    return _html(start_response, "200 OK", body)


def get_logout(environ, start_response):
    session_id = sessions.get_session_id_from_environ(environ)
    session = sessions.get_session(session_id) if session_id else None
    if session is None:
        return unauthorized_page(environ, start_response)

    sessions.delete_session(session_id)
    cookie = "sessionId=; Max-Age=0; Path=/; HttpOnly; SameSite=Strict"
    body = _render("logout.html", user_email=None)
    return _html(start_response, "200 OK", body, extra_headers=[("Set-Cookie", cookie)])
