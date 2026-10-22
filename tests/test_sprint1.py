from datetime import timedelta
import pytest
from helpdesk.cli import seed
from helpdesk.config import configuration
from helpdesk.models import db, LoginBucket, LoginSession, Task, Ticket, User, utcnow
from conftest import csrf, login


@pytest.mark.parametrize("role", ["solicitante", "tecnico"])
def test_valid_login(client, app, role):
    response = login(client, role)
    assert response.status_code == 303
    assert client.get("/").status_code == 200
    cookie = response.headers["Set-Cookie"]
    assert "HttpOnly" in cookie and "SameSite=Lax" in cookie and "Expires=" in cookie
    with app.app_context():
        user = db.session.scalar(db.select(User).where(User.role == role))
        assert user.password_hash.startswith("scrypt:") and user.password_hash != "test-password"


def test_invalid_login_generic(client, app):
    a = login(client, password="incorrect")
    b = login(client, email="unknown@example.com", password="incorrect")
    assert "E-mail ou senha inválidos." in a.text and "E-mail ou senha inválidos." in b.text
    assert client.get("/").status_code == 302
    with app.app_context():
        assert db.session.query(LoginSession).count() == 0


@pytest.mark.parametrize("path", ["/", "/chamados/novo", "/kanban"])
def test_private_routes_anonymous(client, path):
    response = client.get(path)
    assert response.status_code == 302 and "/login?next=" in response.location


def test_logout_revokes_even_copied_cookie(client, app):
    login(client)
    old_cookie = client.get_cookie("session").value
    assert client.get("/logout").status_code == 405
    response = client.post("/logout", data={"csrf_token": csrf(client, "/")})
    assert response.status_code == 303 and client.get("/").status_code == 302
    client.set_cookie("session", old_cookie)
    assert client.get("/").status_code == 302
    with app.app_context():
        assert db.session.query(LoginSession).count() == 0


def test_ticket_correct_author_status_utc_and_prg(client, app, valid_ticket):
    login(client)
    before = utcnow()
    response = client.post("/chamados/novo", data={**valid_ticket, "requester_id": 999,
        "status": "Encerrado", "csrf_token": csrf(client, "/chamados/novo")})
    assert response.status_code == 303
    page = client.get(response.location)
    assert page.status_code == 200 and "Chamado registrado com sucesso" in page.text
    assert "HD-" in page.text and "UTC" in page.text
    client.get(response.location)
    with app.app_context():
        tickets = db.session.scalars(db.select(Ticket)).all()
        assert len(tickets) == 1
        ticket = tickets[0]
        assert ticket.requester_id == db.session.scalar(db.select(User.id).where(User.email == "solicitante@example.com"))
        assert ticket.status == "Aberto" and before <= ticket.opened_at <= utcnow()
        assert len(ticket.id) == 36


@pytest.mark.parametrize("field,value", [("title", ""), ("title", "abcd"), ("title", "x" * 121),
    ("description", ""), ("description", "123456789"), ("description", "x" * 5001),
    ("category", ""), ("category", "Inexistente"), ("title", "     ")])
def test_invalid_ticket(client, app, valid_ticket, field, value):
    login(client)
    response = client.post("/chamados/novo", data={**valid_ticket, field: value,
        "csrf_token": csrf(client, "/chamados/novo")})
    assert response.status_code == 422
    with app.app_context():
        assert db.session.query(Ticket).count() == 0


def test_ticket_boundaries_and_escape(client, app, valid_ticket):
    login(client)
    title = "<script>alert(1)</script>"
    response = client.post("/chamados/novo", data={**valid_ticket, "title": title,
        "description": "<script>" + "á" * 4983 + "</script>", "csrf_token": csrf(client, "/chamados/novo")})
    assert response.status_code == 303
    page = client.get(response.location)
    assert "<script>" not in page.text and "&lt;script&gt;" in page.text
    response = client.post("/chamados/novo", data={**valid_ticket, "title": "a" * 120,
        "description": "b" * 5000, "csrf_token": csrf(client, "/chamados/novo")})
    assert response.status_code == 303


@pytest.mark.parametrize("path", ["/login", "/logout", "/chamados/novo", "/kanban/S1-01/mover"])
def test_csrf_missing_or_invalid(client, path):
    for data in ({}, {"csrf_token": "invalid"}):
        assert client.post(path, data=data).status_code == 400


def test_other_requester_cannot_read_ticket(client, app, valid_ticket):
    login(client)
    response = client.post("/chamados/novo", data={**valid_ticket, "csrf_token": csrf(client, "/chamados/novo")})
    location = response.location
    client.post("/logout", data={"csrf_token": csrf(client, "/")})
    login(client, email="outra@example.com")
    assert client.get(location).status_code == 404
    assert client.get("/chamados/00000000-0000-0000-0000-000000000000").status_code == 404


def test_technician_cannot_create_or_read_ticket(client, valid_ticket):
    login(client, "tecnico")
    assert client.get("/chamados/novo").status_code == 403
    assert client.post("/chamados/novo", data={**valid_ticket, "csrf_token": csrf(client, "/")}).status_code == 403
    assert client.get("/chamados/00000000-0000-0000-0000-000000000000").status_code == 403


def test_kanban_requester_denied(client):
    login(client)
    assert client.get("/kanban").status_code == 403
    assert client.post("/kanban/S1-01/mover", data={"column": "Concluído", "csrf_token": csrf(client, "/")}).status_code == 403


def test_kanban_move_persists_and_invalid_column(client, app):
    login(client, "tecnico")
    assert client.get("/kanban").status_code == 200
    response = client.post("/kanban/S1-01/mover", data={"column": "A fazer", "csrf_token": csrf(client, "/kanban")})
    assert response.status_code == 303
    with app.app_context():
        db.session.remove()
        assert db.session.get(Task, "S1-01").column == "A fazer"
    client.post("/kanban/S1-01/mover", data={"column": "Inválida", "csrf_token": csrf(client, "/kanban")})
    with app.app_context():
        assert db.session.get(Task, "S1-01").column == "A fazer"
    assert client.post("/kanban/unknown/mover", data={"column": "A fazer", "csrf_token": csrf(client, "/kanban")}).status_code == 404


def test_seed_idempotent_preserves_password_column_and_extra_tasks(app):
    with app.app_context():
        original = {u.id: u.password_hash for u in db.session.scalars(db.select(User))}
        db.session.get(Task, "S1-01").column = "Backlog"
        db.session.add(Task(id="EXTRA", title="Extra", sprint=1, priority="Baixa", acceptance="Preservar", column="A fazer"))
        db.session.commit()
        count = db.session.query(Task).count()
        credentials = (app.config["STATE_DIR"] / "demo-credentials.json").read_text()
        seed()
        seed()
        assert original == {u.id: u.password_hash for u in db.session.scalars(db.select(User))}
        assert db.session.query(Task).count() == count
        assert db.session.get(Task, "S1-01").column == "Backlog"
        assert db.session.get(Task, "EXTRA") is not None
        assert (app.config["STATE_DIR"] / "demo-credentials.json").read_text() == credentials
        assert (app.config["STATE_DIR"] / "demo-credentials.json").stat().st_mode & 0o777 == 0o600


def test_throttle_persistent_and_expiry(client, app):
    for _ in range(5):
        assert login(client, password="wrong").status_code == 200
    assert login(client).status_code == 429
    another_client = app.test_client()
    assert login(another_client).status_code == 429
    with app.app_context():
        for bucket in db.session.scalars(db.select(LoginBucket)):
            bucket.started_at = utcnow() - timedelta(minutes=11)
        db.session.commit()
    assert login(client).status_code == 303


@pytest.mark.parametrize("target", ["https://evil.example", "//evil.example", "/\\evil.example", "/%2f%2fevil.example", "/login", "javascript:alert(1)", "//["])
def test_no_open_redirect(client, target):
    from urllib.parse import quote
    response = login(client, next_url="?next=" + quote(target, safe=""))
    assert response.status_code == 303 and response.location == "/"


def test_safe_next(client):
    assert login(client, next_url="?next=/chamados/novo").location == "/chamados/novo"


def test_expired_session_denied(client, app):
    login(client)
    with app.app_context():
        db.session.scalar(db.select(LoginSession)).expires_at = utcnow() - timedelta(seconds=1)
        db.session.commit()
    assert client.get("/").status_code == 302


def test_health_and_headers(client, app):
    response = client.get("/healthz")
    assert response.status_code == 200 and response.json == {"status": "ok"}
    assert response.headers["X-Content-Type-Options"] == "nosniff"
    assert "script-src 'none'" in response.headers["Content-Security-Policy"]
    with app.app_context():
        db.session.execute(db.text("DROP TABLE tasks"))
        db.session.commit()
    assert client.get("/healthz").status_code == 503


def test_login_field_limits(client):
    for field, value in (("email", "a" * 255 + "@example.com"), ("password", "a" * 129), ("email", "not-an-email")):
        data = {"email": "solicitante@example.com", "password": "test-password", field: value,
                "csrf_token": csrf(client, "/login")}
        assert client.post("/login", data=data).status_code == 422
    assert client.post("/login", data=b"x" * 40000, content_type="application/x-www-form-urlencoded").status_code == 413


def test_secret_persisted_and_https_configuration(tmp_path, monkeypatch):
    monkeypatch.setenv("HELPDESK_STATE_DIR", str(tmp_path))
    monkeypatch.delenv("SECRET_KEY", raising=False)
    config = configuration()
    assert config["SECRET_KEY"] == configuration()["SECRET_KEY"]
    assert (tmp_path / "session.key").stat().st_mode & 0o777 == 0o600
    assert config["SESSION_COOKIE_SECURE"] is False
    monkeypatch.setenv("COOKIE_SECURE", "true")
    assert configuration()["SESSION_COOKIE_SECURE"] is True
    monkeypatch.setenv("SECRET_KEY", "short")
    with pytest.raises(RuntimeError):
        configuration()


def test_demo_cli_only_explicit(app):
    result = app.test_cli_runner().invoke(args=["demo-credentials"])
    assert result.exit_code == 0 and "solicitante@example.com" in result.output
    seed_result = app.test_cli_runner().invoke(args=["seed"])
    assert "Senha" not in seed_result.output


def test_ip_limit_applies_across_accounts(client, app):
    from helpdesk.security import bucket_keys
    with app.test_request_context(environ_base={"REMOTE_ADDR": "127.0.0.1"}):
        ip_key = bucket_keys("unknown@example.com")[1][0]
        db.session.add(LoginBucket(key=ip_key, failures=29, started_at=utcnow()))
        db.session.commit()
    assert login(client, email="unknown@example.com", password="wrong").status_code == 200
    assert login(client).status_code == 429


def test_invalid_csrf_does_not_logout_active_user(client):
    login(client)
    assert client.post("/logout").status_code == 400
    assert client.get("/").status_code == 200
