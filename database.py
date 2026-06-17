from datetime import datetime

users: dict[str, dict] = {}
# users[email] = {"salt": str, "password_hash": str}

sessions: dict[str, dict] = {}
# sessions[session_id] = {"email": str, "created_at": datetime, "views": int}
