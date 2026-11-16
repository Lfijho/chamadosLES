"""Consultas autorizadas e gravações transacionais dos chamados."""
from sqlalchemy.orm.exc import StaleDataError
from flask import abort
from .models import db, Ticket, StatusEvent, TicketNote, User, STATUSES, PRIORITIES

PAGE_SIZE = 10


def visible_tickets(user):
    query = db.select(Ticket)
    if user.role == "solicitante":
        return query.where(Ticket.requester_id == user.id)
    if user.role != "tecnico":
        abort(403)
    return query


def list_tickets(user, status="", category="", page=1):
    query = visible_tickets(user)
    if status:
        query = query.where(Ticket.status == status)
    if category:
        query = query.where(Ticket.category == category)
    return db.paginate(query.order_by(Ticket.opened_at.desc(), Ticket.id.desc()),
                       page=page, per_page=PAGE_SIZE, max_per_page=PAGE_SIZE, error_out=True)


def get_ticket(ticket_id, user):
    return db.session.scalar(visible_tickets(user).where(Ticket.id == str(ticket_id)))


def create_ticket(user, title, description, category):
    if user.role != "solicitante":
        abort(403)
    ticket = Ticket(requester_id=user.id, title=title, description=description, category=category)
    db.session.add(ticket)
    db.session.commit()
    return ticket


def check_edit(ticket, user, version):
    if user.role != "tecnico":
        abort(403)
    if ticket.version != version:
        raise StaleDataError("O chamado mudou. Recarregue a página antes de tentar novamente.")
    if ticket.status == "Concluído":
        raise ValueError("Chamados concluídos não podem ser alterados.")


def update_priority(ticket, user, priority, version):
    check_edit(ticket, user, version)
    ticket.set_priority(priority)
    db.session.commit()


def update_status(ticket, user, new_status, solution, version):
    check_edit(ticket, user, version)
    previous = ticket.status
    ticket.change_status(new_status, solution)
    event = StatusEvent(ticket=ticket, actor=user, old_status=previous, new_status=ticket.status)
    db.session.add(event)
    db.session.commit()


def get_history(ticket, user):
    """Cronologia real; em empate, status precede anotação, seguido pelo id."""
    if user.role not in ("solicitante", "tecnico"):
        abort(403)
    if user.role == "solicitante" and ticket.requester_id != user.id:
        abort(404)
    statuses = db.select(
        StatusEvent.id.label("id"), StatusEvent.occurred_at.label("occurred_at"),
        db.literal(0).label("event_order"), db.literal("status").label("kind"),
        User.name.label("author"), db.literal(None, type_=db.Text).label("content"),
        StatusEvent.old_status.label("old_status"), StatusEvent.new_status.label("new_status"),
    ).join(User, User.id == StatusEvent.actor_id).where(StatusEvent.ticket_id == ticket.id)
    notes = db.select(
        TicketNote.id, TicketNote.occurred_at, db.literal(1), db.literal("note"),
        User.name, TicketNote.content, db.literal(None), db.literal(None),
    ).join(User, User.id == TicketNote.author_id).where(TicketNote.ticket_id == ticket.id)
    history = statuses.union_all(notes).subquery()
    return db.session.execute(db.select(history).order_by(
        history.c.occurred_at, history.c.event_order, history.c.id)).mappings().all()


def add_note(ticket, user, content):
    """Inclui registro sem modificar os dados ou a versão do chamado."""
    if user.role != "tecnico":
        abort(403)
    cleaned = (content or "").strip()
    if not cleaned or len(cleaned) > 5000:
        raise ValueError("Informe uma anotação com 1 a 5.000 caracteres.")
    note = TicketNote(ticket=ticket, author=user, content=cleaned)
    db.session.add(note)
    db.session.commit()
    return note


def get_indicators(user):
    """Conta chamados sem juntar eventos ou anotações à consulta."""
    if user.role != "tecnico":
        abort(403)
    statuses = dict(db.session.execute(db.select(
        Ticket.status, db.func.count(Ticket.id)).group_by(Ticket.status)).all())
    priorities = dict(db.session.execute(db.select(
        Ticket.priority, db.func.count(Ticket.id)).group_by(Ticket.priority)).all())
    return {"status": {name: statuses.get(name, 0) for name in STATUSES},
            "priority": {name: priorities.get(name, 0) for name in PRIORITIES}}
