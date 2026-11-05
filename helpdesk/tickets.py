"""Consultas autorizadas e gravações transacionais dos chamados."""
from sqlalchemy.orm.exc import StaleDataError
from flask import abort
from .models import db, Ticket, StatusEvent

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
