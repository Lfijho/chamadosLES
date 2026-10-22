from flask import Blueprint, abort, flash, g, redirect, render_template, request, session, url_for
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from .forms import LoginForm, MoveTaskForm, TicketForm
from .models import COLUMNS, db, LoginBucket, LoginSession, Task, Ticket, User, utcnow
from .security import (authenticate, bucket_keys, failed_login, is_limited,
                       require_user, safe_next, start_session, token_hash)

bp = Blueprint("web", __name__)


def load_user():
    g.user = None
    token = session.get("token")
    if token:
        record = db.session.get(LoginSession, token_hash(token))
        if record and record.expires_at > utcnow():
            g.user = record.user
        else:
            session.clear()


@bp.route("/login", methods=["GET", "POST"])
def login():
    if g.user:
        return redirect(url_for("web.home"))
    form = LoginForm()
    status = 200
    if form.validate_on_submit():
        email = form.email.data.lower()
        keys = bucket_keys(email)
        if is_limited(keys):
            flash("Muitas tentativas de acesso. Aguarde até 10 minutos e tente novamente.", "error")
            status = 429
        else:
            user = db.session.scalar(db.select(User).where(User.email == email))
            if authenticate(user, form.password.data):
                # Sucesso limpa apenas o contador da conta, preservando o limite por IP.
                db.session.execute(db.delete(LoginBucket).where(LoginBucket.key == keys[0][0]))
                start_session(user)
                return redirect(safe_next(request.args.get("next")) or url_for("web.home"), code=303)
            failed_login(keys)
            flash("E-mail ou senha inválidos.", "error")
    elif request.method == "POST":
        status = 422
    response = render_template("login.html", form=form)
    if status == 429:
        return response, status, {"Retry-After": "600"}
    return response, status


@bp.post("/logout")
@require_user()
def logout():
    record = db.session.get(LoginSession, token_hash(session["token"]))
    if record:
        db.session.delete(record)
        db.session.commit()
    session.clear()
    flash("Você saiu da sua conta.", "success")
    return redirect(url_for("web.login"), code=303)


@bp.get("/")
@require_user()
def home():
    return render_template("home.html")


@bp.route("/chamados/novo", methods=["GET", "POST"])
@require_user("solicitante")
def new_ticket():
    form = TicketForm()
    if form.validate_on_submit():
        ticket = Ticket(requester_id=g.user.id, title=form.title.data,
                        description=form.description.data, category=form.category.data)
        db.session.add(ticket)
        db.session.commit()
        return redirect(url_for("web.ticket_confirmation", ticket_id=ticket.id), code=303)
    return render_template("new_ticket.html", form=form), 422 if request.method == "POST" else 200


@bp.get("/chamados/<uuid:ticket_id>")
@require_user("solicitante")
def ticket_confirmation(ticket_id):
    ticket = db.session.get(Ticket, str(ticket_id))
    if ticket is None or ticket.requester_id != g.user.id:
        abort(404)
    return render_template("confirmation.html", ticket=ticket)


@bp.get("/kanban")
@require_user("tecnico")
def kanban():
    tasks = db.session.scalars(db.select(Task).order_by(Task.sprint, Task.id)).all()
    return render_template("kanban.html", columns=COLUMNS, tasks=tasks, form=MoveTaskForm())


@bp.post("/kanban/<task_id>/mover")
@require_user("tecnico")
def move_task(task_id):
    task = db.get_or_404(Task, task_id)
    form = MoveTaskForm()
    if not form.validate_on_submit():
        flash("Coluna inválida. Selecione uma das opções do quadro.", "error")
        return redirect(url_for("web.kanban"), code=303)
    task.column = form.column.data
    db.session.commit()
    flash(f"Tarefa {task.id} movida para {task.column}.", "success")
    return redirect(url_for("web.kanban", _anchor=task.id), code=303)


@bp.get("/healthz")
def health():
    try:
        db.session.execute(text("SELECT version_num FROM alembic_version")).one()
        db.session.execute(db.select(User.id).limit(1)).first()
        db.session.execute(db.select(Task.id).limit(1)).first()
    except SQLAlchemyError:
        db.session.rollback()
        return {"status": "unavailable"}, 503
    return {"status": "ok"}
