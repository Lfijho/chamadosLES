"""Persistência da Sprint 1. Datas sem offset no SQLite representam UTC."""
from datetime import datetime, timezone
import uuid
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash, generate_password_hash

db = SQLAlchemy()
CATEGORIES = ("Hardware", "Software", "Rede", "Acessos", "Outros")
COLUMNS = ("Backlog", "A fazer", "Em andamento", "Concluído")


def utcnow():
    return datetime.now(timezone.utc).replace(tzinfo=None)


class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(254), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), nullable=False)
    __table_args__ = (db.CheckConstraint("role IN ('solicitante', 'tecnico')", name="user_role"),)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password, method="scrypt")

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class LoginSession(db.Model):
    __tablename__ = "login_sessions"
    token_hash = db.Column(db.String(64), primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    expires_at = db.Column(db.DateTime, nullable=False)
    user = db.relationship(User)


class LoginBucket(db.Model):
    __tablename__ = "login_buckets"
    key = db.Column(db.String(64), primary_key=True)
    failures = db.Column(db.Integer, nullable=False, default=0)
    started_at = db.Column(db.DateTime, nullable=False)


class Ticket(db.Model):
    __tablename__ = "tickets"
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    requester_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    title = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(20), nullable=False)
    status = db.Column(db.String(20), nullable=False, default="Aberto")
    opened_at = db.Column(db.DateTime, nullable=False, default=utcnow)
    __table_args__ = (
        db.CheckConstraint("length(title) BETWEEN 5 AND 120", name="ticket_title_length"),
        db.CheckConstraint("length(description) BETWEEN 10 AND 5000", name="ticket_description_length"),
        db.CheckConstraint("category IN ('Hardware','Software','Rede','Acessos','Outros')", name="ticket_category"),
        db.CheckConstraint("status = 'Aberto'", name="ticket_initial_status"),
    )

    @property
    def protocol(self):
        return "HD-" + self.id.upper()


class Task(db.Model):
    __tablename__ = "tasks"
    id = db.Column(db.String(20), primary_key=True)
    title = db.Column(db.String(160), nullable=False)
    sprint = db.Column(db.Integer, nullable=False)
    priority = db.Column(db.String(20), nullable=False)
    acceptance = db.Column(db.Text, nullable=False)
    column = db.Column(db.String(20), nullable=False, default="Backlog")
    __table_args__ = (db.CheckConstraint('"column" IN (\'Backlog\',\'A fazer\',\'Em andamento\',\'Concluído\')', name="task_column"),)
