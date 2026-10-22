import os
import secrets
from datetime import timedelta
from pathlib import Path


def configuration():
    state = Path(os.environ.get("HELPDESK_STATE_DIR", "/data"))
    state.mkdir(mode=0o700, parents=True, exist_ok=True)
    secret = os.environ.get("SECRET_KEY")
    if secret is not None and len(secret) < 32:
        raise RuntimeError("SECRET_KEY precisa de pelo menos 32 caracteres aleatórios.")
    if secret is None:
        path = state / "session.key"
        if not path.exists():
            # Um processo de provisionamento; O_EXCL impede sobrescrever uma chave existente.
            try:
                fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
            except FileExistsError:
                pass
            else:
                with os.fdopen(fd, "w") as stream:
                    stream.write(secrets.token_hex(32))
        secret = path.read_text().strip()
        if len(secret) < 32:
            raise RuntimeError("Chave persistida inválida; verifique o volume de estado.")
    return dict(
        SECRET_KEY=secret,
        STATE_DIR=state,
        SQLALCHEMY_DATABASE_URI=os.environ.get("DATABASE_URL", f"sqlite:///{state / 'helpdesk.sqlite'}"),
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        SQLALCHEMY_ENGINE_OPTIONS={"connect_args": {"timeout": 15}, "hide_parameters": True},
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE="Lax",
        SESSION_COOKIE_SECURE=os.environ.get("COOKIE_SECURE", "false").lower() == "true",
        PERMANENT_SESSION_LIFETIME=timedelta(hours=8),
        SESSION_REFRESH_EACH_REQUEST=False,
        MAX_CONTENT_LENGTH=32 * 1024,
        WTF_CSRF_TIME_LIMIT=8 * 60 * 60,
    )
