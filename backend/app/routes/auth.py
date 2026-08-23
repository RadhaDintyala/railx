import base64
import hashlib
import hmac
import json
import secrets
import uuid
from datetime import datetime, timedelta, timezone

from starlette.responses import JSONResponse

from ..config import settings
from ..database.database import get_connection
from ..database.postgres import create_postgres_user, get_postgres_user, postgres_is_ready


def _hash_password(password, salt=None):
    salt = salt or secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 240000)
    return f"pbkdf2_sha256$240000${base64.urlsafe_b64encode(salt).decode()}${base64.urlsafe_b64encode(digest).decode()}"


def _check_password(password, stored):
    try:
        _, rounds, encoded_salt, encoded_digest = stored.split("$")
        salt = base64.urlsafe_b64decode(encoded_salt.encode())
        digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, int(rounds))
        return hmac.compare_digest(base64.urlsafe_b64encode(digest).decode(), encoded_digest)
    except (ValueError, TypeError):
        return False


def _find_user(email):
    if settings.database_url.startswith("postgresql") and postgres_is_ready():
        return get_postgres_user(email)
    with get_connection() as conn:
        row = conn.execute("SELECT * FROM users WHERE lower(email) = lower(?)", (email,)).fetchone()
        return dict(row) if row else None


def _create_user(user):
    if settings.database_url.startswith("postgresql") and postgres_is_ready():
        create_postgres_user(user)
        return
    with get_connection() as conn:
        conn.execute("INSERT INTO users (id, name, email, phone, password_hash) VALUES (?, ?, ?, ?, ?)", tuple(user[key] for key in ("id", "name", "email", "phone", "password_hash")))


def _public_user(user):
    return {"id": user["id"], "name": user["name"], "email": user["email"], "phone": user.get("phone")}


def _encode_token(user):
    payload = {"sub": user["id"], "email": user["email"], "exp": int((datetime.now(timezone.utc) + timedelta(days=7)).timestamp())}
    body = base64.urlsafe_b64encode(json.dumps(payload, separators=(",", ":")).encode()).decode().rstrip("=")
    signature = hmac.new(settings.auth_secret.encode(), body.encode(), hashlib.sha256).digest()
    return f"{body}.{base64.urlsafe_b64encode(signature).decode().rstrip('=')}"

def _authenticated_user(request):
    header = request.headers.get("authorization", "")
    token = header[7:] if header.lower().startswith("bearer ") else ""
    try:
        body, encoded_signature = token.split(".", 1)
        expected = hmac.new(settings.auth_secret.encode(), body.encode(), hashlib.sha256).digest()
        signature = base64.urlsafe_b64decode(encoded_signature + "=" * (-len(encoded_signature) % 4))
        if not hmac.compare_digest(signature, expected):
            return None
        payload = json.loads(base64.urlsafe_b64decode(body + "=" * (-len(body) % 4)))
        if int(payload["exp"]) <= int(datetime.now(timezone.utc).timestamp()):
            return None
        return _find_user(payload["email"])
    except (ValueError, TypeError, KeyError, json.JSONDecodeError):
        return None

def _response(user):
    return JSONResponse({"token": _encode_token(user), "user": _public_user(user)})

async def me(request):
    user = _authenticated_user(request)
    return JSONResponse({"user": _public_user(user)} if user else {"error": "Invalid or expired session."}, status_code=200 if user else 401)


async def signup(request):
    try:
        payload = await request.json()
    except ValueError:
        return JSONResponse({"error": "Invalid JSON body"}, status_code=400)
    name = str(payload.get("name", "")).strip()
    email = str(payload.get("email", "")).strip().lower()
    phone = str(payload.get("phone", "")).strip() or None
    password = str(payload.get("password", ""))
    if len(name) < 2 or "@" not in email or len(password) < 6:
        return JSONResponse({"error": "Enter a valid name, email, and password of at least 6 characters."}, status_code=400)
    if _find_user(email):
        return JSONResponse({"error": "An account with that email already exists."}, status_code=409)
    user = {"id": str(uuid.uuid4()), "name": name, "email": email, "phone": phone, "password_hash": _hash_password(password), "created_at": datetime.now(timezone.utc)}
    _create_user(user)
    return _response(user)


async def login(request):
    try:
        payload = await request.json()
    except ValueError:
        return JSONResponse({"error": "Invalid JSON body"}, status_code=400)
    email = str(payload.get("email", "")).strip().lower()
    password = str(payload.get("password", ""))
    user = _find_user(email)
    if not user or not _check_password(password, user["password_hash"]):
        return JSONResponse({"error": "Invalid email or password."}, status_code=401)
    return _response(user)
