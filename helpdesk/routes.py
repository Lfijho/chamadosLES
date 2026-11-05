from flask import Blueprint, abort, flash, g, redirect, render_template, request, session, url_for
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm.exc import StaleDataError
from .forms import LoginForm, MoveTaskForm, TicketForm, TicketFilterForm, PriorityForm, StatusForm
from .models import COLUMNS, db, LoginBucket, LoginSession, StatusEvent, Task, Ticket, User, utcnow
from .security import (authenticate, bucket_keys, failed_login, is_limited,
                       require_user, safe_next, start_session, token_hash)
from . import tickets

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
        ticket = tickets.create_ticket(g.user, form.title.data, form.description.data, form.category.data)
        return redirect(url_for("web.ticket_confirmation", ticket_id=ticket.id), code=303)
    return render_template("new_ticket.html", form=form), 422 if request.method == "POST" else 200


@bp.get("/chamados/<uuid:ticket_id>")
@require_user("solicitante")
def ticket_confirmation(ticket_id):
    ticket = tickets.get_ticket(ticket_id, g.user)
    if ticket is None:
        abort(404)
    return render_template("confirmation.html", ticket=ticket)


@bp.get("/chamados")
@require_user()
def ticket_list():
    form = TicketFilterForm(formdata=request.args)
    valid = form.validate()
    for name in ("status", "category", "page"):
        if len(request.args.getlist(name)) > 1:
            getattr(form, name).errors.append("Informe apenas um valor para este campo.")
            valid = False
    pagination = tickets.list_tickets(g.user, form.status.data, form.category.data, form.page.data) if valid else None
    return render_template("ticket_list.html", form=form, pagination=pagination,
                           filtered=bool(form.status.data or form.category.data)), 200 if valid else 422


def ticket_detail_response(ticket, priority_form=None, status_form=None, code=200):
    priority_form = priority_form or PriorityForm(formdata=None, priority=ticket.priority, version=ticket.version)
    next_status = {"Aberto": "Em atendimento", "Em atendimento": "Concluído"}.get(ticket.status)
    status_form = status_form or StatusForm(formdata=None, status=next_status, version=ticket.version)
    status_form.status.choices = [(next_status, next_status)] if next_status else []
    return render_template("ticket_detail.html", ticket=ticket, priority_form=priority_form,
                           status_form=status_form, next_status=next_status), code


@bp.get("/chamados/<uuid:ticket_id>/detalhes")
@require_user()
def ticket_detail(ticket_id):
    ticket = tickets.get_ticket(ticket_id, g.user)
    if ticket is None:
        abort(404)
    return ticket_detail_response(ticket)


@bp.post("/chamados/<uuid:ticket_id>/prioridade")
@require_user("tecnico")
def ticket_priority(ticket_id):
    ticket = tickets.get_ticket(ticket_id, g.user)
    if ticket is None:
        abort(404)
    form = PriorityForm()
    if not form.validate_on_submit():
        return ticket_detail_response(ticket, priority_form=form, code=422)
    try:
        tickets.update_priority(ticket, g.user, form.priority.data, form.version.data)
    except StaleDataError:
        db.session.rollback()
        flash("O chamado mudou. Confira os dados atualizados antes de tentar novamente.", "error")
        return ticket_detail_response(ticket, code=409)
    except ValueError as error:
        db.session.rollback()
        form.priority.errors.append(str(error))
        return ticket_detail_response(ticket, priority_form=form, code=422)
    except SQLAlchemyError:
        db.session.rollback()
        abort(500)
    flash("Prioridade atualizada.", "success")
    return redirect(url_for("web.ticket_detail", ticket_id=ticket.id), code=303)


@bp.post("/chamados/<uuid:ticket_id>/status")
@require_user("tecnico")
def ticket_status(ticket_id):
    ticket = tickets.get_ticket(ticket_id, g.user)
    if ticket is None:
        abort(404)
    form = StatusForm()
    if not form.validate_on_submit():
        return ticket_detail_response(ticket, status_form=form, code=422)
    try:
        tickets.update_status(ticket, g.user, form.status.data, form.solution.data, form.version.data)
    except StaleDataError:
        db.session.rollback()
        flash("O chamado mudou. Confira os dados atualizados antes de tentar novamente.", "error")
        return ticket_detail_response(ticket, code=409)
    except ValueError as error:
        db.session.rollback()
        form.status.errors.append(str(error))
        return ticket_detail_response(ticket, status_form=form, code=422)
    except SQLAlchemyError:
        db.session.rollback()
        abort(500)
    flash("Status atualizado." if ticket.status != "Concluído" else "Chamado concluído com solução registrada.", "success")
    return redirect(url_for("web.ticket_detail", ticket_id=ticket.id), code=303)


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
        db.session.execute(db.select(Ticket.priority).limit(1)).first()
        db.session.execute(db.select(StatusEvent.id).limit(1)).first()
    except SQLAlchemyError:
        db.session.rollback()
        return {"status": "unavailable"}, 503
    return {"status": "ok"}
