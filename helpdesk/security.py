"""Sessões revogáveis e limite persistente para uma única instância."""
from datetime import timedelta
from functools import wraps
import hashlib
import hmac
import secrets
from urllib.parse import urlsplit
from flask import abort, current_app, g, redirect, request, session, url_for
from sqlalchemy.dialects.sqlite import insert
from werkzeug.security import check_password_hash, generate_password_hash
from .models import db, LoginBucket, LoginSession, utcnow

DUMMY_HASH = generate_password_hash(secrets.token_urlsafe(24), method="scrypt")
WINDOW = timedelta(minutes=10)


def token_hash(token):
    return hashlib.sha256(token.encode()).hexdigest()


def require_user(role=None):
    def decorate(view):
        @wraps(view)
        def protected(*args, **kwargs):
            if g.user is None:
                return redirect(url_for("web.login", next=request.path))
            if role and g.user.role != role:
                abort(403)
            return view(*args, **kwargs)
        return protected
    return decorate


def safe_next(target):
    if not target or any(ord(c) < 32 for c in target) or "\\" in target:
        return None
    if not target.startswith("/") or target.startswith("//"):
        return None
    parts = urlsplit(target)
    if parts.scheme or parts.netloc:
        return None
    # Redirecionar somente para caminhos conhecidos evita ambiguidades do navegador.
    if parts.path not in ("/", "/chamados/novo", "/kanban"):
        return None
    return parts.path


def bucket_keys(email):
    key = current_app.secret_key.encode()
    return [(hmac.new(key, value.encode(), "sha256").hexdigest(), limit)
            for value, limit in (("email:" + email, 5), ("ip:" + (request.remote_addr or "unknown"), 30))]


def is_limited(keys):
    db.session.execute(db.delete(LoginBucket).where(LoginBucket.started_at <= utcnow() - WINDOW))
    db.session.commit()
    return any((bucket := db.session.get(LoginBucket, key)) is not None and bucket.failures >= limit
               for key, limit in keys)


def failed_login(keys):
    for key, _ in keys:
        statement = insert(LoginBucket).values(key=key, failures=1, started_at=utcnow())
        db.session.execute(statement.on_conflict_do_update(index_elements=["key"],
                           set_={"failures": LoginBucket.failures + 1}))
    db.session.commit()


def authenticate(user, password):
    return user.check_password(password) if user else check_password_hash(DUMMY_HASH, password)


def start_session(user):
    session.clear()
    session.permanent = True
    token = secrets.token_urlsafe(32)
    session["token"] = token
    db.session.execute(db.delete(LoginSession).where(LoginSession.expires_at <= utcnow()))
    db.session.add(LoginSession(token_hash=token_hash(token), user_id=user.id,
                              expires_at=utcnow() + current_app.permanent_session_lifetime))
    db.session.commit()
