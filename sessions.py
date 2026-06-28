import uuid
from datetime import datetime, timedelta

import database

SESSION_DURATION = timedelta(minutes=30)


def create_session(email: str) -> str:
    session_id = str(uuid.uuid4())
    database.sessions[session_id] = {
        "email": email,
        "created_at": datetime.now(),
        "views": 0,
    }
    return session_id


def get_session(session_id: str) -> dict | None:
    session = database.sessions.get(session_id)
    if session is None:
        return None
    if datetime.now() - session["created_at"] > SESSION_DURATION:
        del database.sessions[session_id]
        return None
    return session


def delete_session(session_id: str | None) -> None:
    database.sessions.pop(session_id, None)


def get_session_id_from_environ(environ) -> str | None:
    cookie_str = environ.get("HTTP_COOKIE", "")
    for part in cookie_str.split(";"):
        part = part.strip()
        if part.startswith("sessionId="):
            return part[len("sessionId="):]
    return None


def get_authenticated_email(environ) -> str | None:
    session_id = get_session_id_from_environ(environ)
    if not session_id:
        return None
    session = get_session(session_id)
    return session["email"] if session else None
