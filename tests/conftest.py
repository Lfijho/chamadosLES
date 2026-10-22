import re
from html import unescape
from pathlib import Path
import pytest
from flask_migrate import upgrade
from helpdesk import create_app
from helpdesk.cli import seed
from helpdesk.models import db, User


@pytest.fixture()
def app(tmp_path, monkeypatch):
    monkeypatch.setenv("HELPDESK_STATE_DIR", str(tmp_path))
    monkeypatch.setenv("SECRET_KEY", "isolated-test-key-with-at-least-32-characters")
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.delenv("COOKIE_SECURE", raising=False)
    app = create_app()
    app.config.update(TESTING=True)
    with app.app_context():
        upgrade(directory=str(Path(__file__).resolve().parents[1] / "migrations"))
        seed()
        for user in db.session.scalars(db.select(User)):
            user.set_password("test-password")
        another = User(name="Outra pessoa", email="outra@example.com", role="solicitante")
        another.set_password("test-password")
        db.session.add(another)
        db.session.commit()
    yield app
    with app.app_context():
        db.session.remove()
        db.engine.dispose()


@pytest.fixture()
def client(app):
    return app.test_client()


def csrf(client, path):
    response = client.get(path)
    found = re.search(r'name="csrf_token"[^>]*value="([^"]+)"', response.get_data(as_text=True))
    assert found, response.status_code
    return unescape(found.group(1))


def login(client, role="solicitante", email=None, password="test-password", next_url=""):
    return client.post("/login" + next_url, data={"email": email or f"{role}@example.com",
        "password": password, "csrf_token": csrf(client, "/login")})


@pytest.fixture()
def valid_ticket():
    return {"title": "Computador sem rede", "description": "Não consigo acessar a rede desde esta manhã.", "category": "Rede"}
