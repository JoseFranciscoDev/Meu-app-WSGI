import auth
import database
import sessions
from router import Router
from utils import (
    _first,
    _html,
    _read_post_body,
    _render,
)
from wsgiref.types import StartResponse, WSGIEnvironment
from typing import Iterable

router = Router()


def unauthorized_page(environ: WSGIEnvironment, start_response: StartResponse) -> Iterable[bytes]:
    body = _render(
        "feedback.html",
        user_email=None,
        alert_type="warning",
        heading="Acesso não autorizado",
        message="Você precisa fazer login para acessar esta área.",
        actions=[
            {"href": "/login", "label": "Fazer login", "variant": "btn-primary"},
            {"href": "/register", "label": "Criar conta", "variant": "btn-outline-secondary"},
        ],
    )
    return _html(start_response, "401 Unauthorized", body)


def not_found_page(environ: WSGIEnvironment, start_response: StartResponse) -> Iterable[bytes]:
    body = _render(
        "feedback.html",
        user_email=None,
        alert_type="danger",
        heading="Página não encontrada",
        message="A rota solicitada não existe. Usa um dos links providos pela aplicação, paizao",
        actions=[{"href": "/", "label": "Voltar ao início", "variant": "btn-primary"}],
    )
    return _html(start_response, "404 Not Found", body)


@router.get("/")
def get_home_page(environ: WSGIEnvironment, start_response: StartResponse) -> Iterable[bytes]:
    email = sessions.get_authenticated_email(environ)
    body = _render("home.html", user_email=email)
    return _html(start_response, "200 OK", body)


@router.get("/register")
def get_register_page(environ: WSGIEnvironment, start_response: StartResponse) -> Iterable[bytes]:
    body = _render(
        "auth_form.html",
        user_email=None,
        form_title="Criar usuário",
        form_action="/register",
        submit_label="Criar conta",
        min_password_length=8,
    )
    return _html(start_response, "200 OK", body)


@router.post("/register")
def post_register(environ: WSGIEnvironment, start_response: StartResponse) -> Iterable[bytes]:
    form = _read_post_body(environ)
    email = _first(form, "email")
    password = _first(form, "password")

    if email in database.users:
        body = _render(
            "feedback.html",
            user_email=None,
            alert_type="warning",
            heading="Cadastro não concluído",
            message="Já existe um usuário cadastrado com esse e-mail.",
            actions=[
                {"href": "/register", "label": "Tentar novamente", "variant": "btn-primary"},
                {"href": "/login", "label": "Ir para login", "variant": "btn-outline-secondary"},
            ],
        )
        return _html(start_response, "409 Conflict", body)

    salt = auth.generate_salt()
    password_hash = auth.hash_password(password, salt)
    database.users[email] = {"salt": salt, "password_hash": password_hash}

    body = _render(
        "feedback.html",
        user_email=None,
        alert_type="success",
        heading="Usuário criado",
        message="A conta foi criada com sucesso. Agora você já pode fazer login.",
        actions=[{"href": "/login", "label": "Fazer login", "variant": "btn-primary"}],
    )
    return _html(start_response, "200 OK", body)


@router.get("/login")
def get_login_page(environ: WSGIEnvironment, start_response: StartResponse) -> Iterable[bytes]:
    body = _render(
        "auth_form.html",
        user_email=None,
        form_title="Entrar",
        form_action="/login",
        submit_label="Entrar",
    )
    return _html(start_response, "200 OK", body)


@router.post("/login")
def post_login(environ: WSGIEnvironment, start_response: StartResponse) -> Iterable[bytes]:
    form = _read_post_body(environ)
    email = _first(form, "email")
    password = _first(form, "password")

    user = database.users.get(email)
    if user is None:
        body = _render(
            "feedback.html",
            user_email=None,
            alert_type="danger",
            heading="Login inválido",
            message="As credenciais informadas não conferem.",
            actions=[{"href": "/login", "label": "Tentar novamente", "variant": "btn-primary"}],
        )
        return _html(start_response, "401 Unauthorized", body)

    if not auth.verify_password(password, user["salt"], user["password_hash"]):
        body = _render(
            "feedback.html",
            user_email=None,
            alert_type="danger",
            heading="Login inválido",
            message="As credenciais informadas não conferem.",
            actions=[{"href": "/login", "label": "Tentar novamente", "variant": "btn-primary"}],
        )
        return _html(start_response, "401 Unauthorized", body)

    session_id = sessions.create_session(email)
    cookie = f"sessionId={session_id}; HttpOnly; Path=/; SameSite=Strict"
    start_response(
        "302 Found",
        [
            ("Location", "/dashboard"),
            ("Set-Cookie", cookie),
            ("Content-Length", "0"),
        ],
    )
    return [b""]


@router.get("/dashboard")
def get_dashboard(environ: WSGIEnvironment, start_response: StartResponse) -> Iterable[bytes]:
    session_id = sessions.get_session_id_from_environ(environ)
    email = sessions.get_authenticated_email(environ)
    if email is None:
        return unauthorized_page(environ, start_response)
    sessions.increment_views(session_id)
    body = _render("dashboard.html", user_email=email)
    return _html(start_response, "200 OK", body)


@router.get("/admin")
def get_admin(environ: WSGIEnvironment, start_response: StartResponse) -> Iterable[bytes]:
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


@router.get("/logout")
def get_logout(environ: WSGIEnvironment, start_response: StartResponse) -> Iterable[bytes]:
    session_id = sessions.get_session_id_from_environ(environ)
    session = sessions.get_session(session_id) if session_id else None
    if session is None:
        return unauthorized_page(environ, start_response)

    sessions.delete_session(session_id)
    cookie = "sessionId=; Max-Age=0; Path=/; HttpOnly; SameSite=Strict"
    body = _render(
        "feedback.html",
        user_email=None,
        alert_type="success",
        heading="Logout realizado",
        message="A sessão foi encerrada com sucesso.",
        actions=[{"href": "/login", "label": "Fazer login novamente", "variant": "btn-primary"}],
    )
    return _html(start_response, "200 OK", body, extra_headers=[("Set-Cookie", cookie)])
