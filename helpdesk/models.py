"""Persistência da Sprint 1. Datas sem offset no SQLite representam UTC."""
from datetime import datetime, timezone
import uuid
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash, generate_password_hash

db = SQLAlchemy()
CATEGORIES = ("Hardware", "Software", "Rede", "Acessos", "Outros")
COLUMNS = ("Backlog", "A fazer", "Em andamento", "Concluído")
STATUSES = ("Aberto", "Em atendimento", "Concluído")
PRIORITIES = ("Baixa", "Média", "Alta")


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
    priority = db.Column(db.String(10), nullable=False, default="Média", server_default="Média")
    solution = db.Column(db.Text(), nullable=True)
    completed_at = db.Column(db.DateTime(), nullable=True)
    version = db.Column(db.Integer(), nullable=False, default=1, server_default="1")
    requester = db.relationship(User)
    __mapper_args__ = {"version_id_col": version}
    __table_args__ = (
        db.CheckConstraint("length(title) BETWEEN 5 AND 120", name="ticket_title_length"),
        db.CheckConstraint("length(description) BETWEEN 10 AND 5000", name="ticket_description_length"),
        db.CheckConstraint("category IN ('Hardware','Software','Rede','Acessos','Outros')", name="ticket_category"),
        db.CheckConstraint("status IN ('Aberto','Em atendimento','Concluído')", name="ticket_status"),
        db.CheckConstraint("priority IN ('Baixa','Média','Alta')", name="ticket_priority"),
        db.CheckConstraint("version > 0", name="ticket_version"),
        db.CheckConstraint(
            "(status = 'Concluído' AND solution IS NOT NULL AND length(trim(solution)) BETWEEN 1 AND 5000 "
            "AND completed_at IS NOT NULL) OR (status IN ('Aberto','Em atendimento') "
            "AND solution IS NULL AND completed_at IS NULL)", name="ticket_completion"),
    )

    @property
    def protocol(self):
        return "HD-" + self.id.upper()

    def set_priority(self, priority: str) -> None:
        if self.status == "Concluído":
            raise ValueError("Chamados concluídos não podem ser alterados.")
        if priority not in PRIORITIES:
            raise ValueError("Selecione uma prioridade válida.")
        self.priority = priority

    def change_status(self, new_status: str, solution: str = "") -> None:
        next_status = {"Aberto": "Em atendimento", "Em atendimento": "Concluído"}.get(self.status)
        if new_status != next_status or next_status is None:
            raise ValueError("Transição inválida. Siga Aberto → Em atendimento → Concluído.")
        cleaned = (solution or "").strip()
        if new_status == "Concluído":
            if not cleaned or len(cleaned) > 5000:
                raise ValueError("Informe a solução com 1 a 5.000 caracteres para concluir.")
        elif cleaned:
            raise ValueError("Registre a solução somente ao concluir o atendimento.")
        self.status = new_status
        self.solution = cleaned if new_status == "Concluído" else None
        self.completed_at = utcnow() if new_status == "Concluído" else None


class StatusEvent(db.Model):
    __tablename__ = "status_events"
    id = db.Column(db.Integer, primary_key=True)
    ticket_id = db.Column(db.String(36), db.ForeignKey("tickets.id"), nullable=False, index=True)
    actor_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    occurred_at = db.Column(db.DateTime, nullable=False, default=utcnow)
    old_status = db.Column(db.String(20), nullable=False)
    new_status = db.Column(db.String(20), nullable=False)
    ticket = db.relationship(Ticket)
    actor = db.relationship(User)
    __table_args__ = (db.CheckConstraint(
        "(old_status = 'Aberto' AND new_status = 'Em atendimento') OR "
        "(old_status = 'Em atendimento' AND new_status = 'Concluído')", name="event_transition"),)


class Task(db.Model):
    __tablename__ = "tasks"
    id = db.Column(db.String(20), primary_key=True)
    title = db.Column(db.String(160), nullable=False)
    sprint = db.Column(db.Integer, nullable=False)
    priority = db.Column(db.String(20), nullable=False)
    acceptance = db.Column(db.Text, nullable=False)
    description = db.Column(db.Text, nullable=False, default="", server_default="")
    column = db.Column(db.String(20), nullable=False, default="Backlog")
    __table_args__ = (db.CheckConstraint('"column" IN (\'Backlog\',\'A fazer\',\'Em andamento\',\'Concluído\')', name="task_column"),)
