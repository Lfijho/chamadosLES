"""Consulta, atendimento e evolução com estado isolado."""
from datetime import timedelta
from pathlib import Path
import pytest
from flask_migrate import downgrade, upgrade
from sqlalchemy import event
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from sqlalchemy.orm.exc import StaleDataError
from helpdesk.models import db, User, Ticket, StatusEvent, utcnow
from helpdesk import tickets
from conftest import csrf, login


@pytest.fixture()
def ticket_id(app):
    with app.app_context():
        owner = db.session.scalar(db.select(User).where(User.role == "solicitante"))
        ticket = Ticket(requester_id=owner.id, title="Falha de acesso à rede", category="Rede",
                        description="Equipamento não consegue conectar à rede.")
        db.session.add(ticket)
        db.session.commit()
        return ticket.id


def detail(ticket_id):
    return f"/chamados/{ticket_id}/detalhes"


def save(client, app, ticket_id, operation, **fields):
    with app.app_context():
        version = db.session.get(Ticket, ticket_id).version
    return client.post(f"/chamados/{ticket_id}/{operation}", data={
        "csrf_token": csrf(client, detail(ticket_id)), "version": version, **fields})


def snapshot(app, ticket_id):
    with app.app_context():
        db.session.remove()
        t = db.session.get(Ticket, ticket_id)
        return t.status, t.priority, t.solution, t.completed_at, t.version, db.session.query(StatusEvent).count()


def test_list_detail_and_ownership(client, app, ticket_id):
    login(client)
    assert "Falha de acesso à rede" in client.get("/chamados").text
    page = client.get(detail(ticket_id))
    assert page.status_code == 200 and "Média" in page.text and "Solicitante demonstração" in page.text
    other = app.test_client()
    login(other, email="outra@example.com")
    assert "Falha de acesso à rede" not in other.get("/chamados?requester_id=1").text
    assert other.get(detail(ticket_id)).status_code == 404
    assert other.get(f"/chamados/{ticket_id}").status_code == 404
    tech = app.test_client()
    login(tech, "tecnico")
    assert "Falha de acesso à rede" in tech.get("/chamados").text
    assert tech.get(detail(ticket_id)).status_code == 200
    assert tech.get(f"/chamados/{ticket_id}").status_code == 403  # Confirmação anterior preservada.


def test_technician_filters_include_other_requesters(client, app, ticket_id):
    with app.app_context():
        owner=db.session.scalar(db.select(User).where(User.email=="outra@example.com"))
        db.session.add(Ticket(requester_id=owner.id,title="Rede de outra pessoa",category="Rede",description="Outra solicitação de rede."))
        db.session.add(Ticket(requester_id=owner.id,title="Software de outra pessoa",category="Software",description="Outra solicitação de software."))
        db.session.commit()
    login(client,"tecnico")
    response=client.get("/chamados?status=Aberto&category=Rede")
    assert response.status_code==200 and response.text.count('class="ticket-row"')==2
    assert "Rede de outra pessoa" in response.text and "Software de outra pessoa" not in response.text


@pytest.mark.parametrize("size", [1,5000])
def test_valid_solution_boundaries(client,app,ticket_id,size):
    login(client,"tecnico")
    assert save(client,app,ticket_id,"status",status="Em atendimento").status_code==303
    assert save(client,app,ticket_id,"status",status="Concluído",solution="x"*size).status_code==303
    assert snapshot(app,ticket_id)[2]=="x"*size


@pytest.mark.parametrize("suffix", ["", "/detalhes"])
def test_anonymous_list_and_detail(app, ticket_id, suffix):
    client = app.test_client()
    path = "/chamados" if not suffix else detail(ticket_id)
    assert client.get(path).status_code == 302


def test_filters_pagination_and_empty(client, app, ticket_id):
    with app.app_context():
        t = db.session.get(Ticket, ticket_id)
        for i in range(12):
            db.session.add(Ticket(requester_id=t.requester_id, title=f"Solicitação de rede {i:02}",
                                 description="Descrição para verificar paginação.", category="Rede",
                                 opened_at=utcnow() + timedelta(minutes=i+1)))
        db.session.add(Ticket(requester_id=t.requester_id, title="Outro software", category="Software",
                             description="Descrição para verificar filtro."))
        db.session.commit()
    login(client)
    first = client.get("/chamados?status=Aberto&category=Rede")
    assert first.status_code == 200 and first.text.count('class="ticket-row"') == 10
    assert "Outro software" not in first.text and "13 chamados encontrados" in first.text
    assert "page=2" in first.text and "category=Rede" in first.text and "status=Aberto" in first.text
    second = client.get("/chamados?status=Aberto&category=Rede&page=2")
    assert second.text.count('class="ticket-row"') == 3 and ticket_id.upper() in second.text
    assert "Nenhum chamado corresponde" in client.get("/chamados?status=Concluído&category=Rede").text
    assert client.get("/chamados?page=9999").status_code == 404
    another = app.test_client()
    login(another, email="outra@example.com")
    assert "Nenhum chamado por aqui" in another.get("/chamados").text
    assert "Falha de acesso" not in another.get("/chamados?category=Rede&status=Aberto").text


@pytest.mark.parametrize("query", ["status=Inexistente", "category=Inexistente", "page=0", "page=-1", "page=x",
                                    "page=1000001", "status=Aberto&status=Concluído", "category=Rede&category=Software", "page=1&page=2"])
def test_invalid_filters(client, query):
    login(client)
    response = client.get("/chamados?" + query)
    assert response.status_code == 422 and "Revise os filtros" in response.text
    assert "Not a valid integer" not in response.text


@pytest.mark.parametrize("priority", ["Baixa", "Média", "Alta"])
def test_technician_priority(client, app, ticket_id, priority):
    login(client, "tecnico")
    result = save(client, app, ticket_id, "prioridade", priority=priority, status="Concluído", solution="Não aplicar")
    assert result.status_code == 303
    state = snapshot(app, ticket_id)
    assert state[0:3] == ("Aberto", priority, None) and state[-1] == 0


@pytest.mark.parametrize("operation,fields", [("prioridade", {"priority":"Urgente"}),
    ("status", {"status":"Concluído", "solution":"Correção informada"}),
    ("status", {"status":"Aberto"}), ("status", {"status":"Inexistente"}),
    ("status", {"status":"Em atendimento", "solution":"Não pode informar antes de concluir"})])
def test_invalid_edits_do_not_change_anything(client, app, ticket_id, operation, fields):
    login(client, "tecnico")
    before = snapshot(app, ticket_id)
    assert save(client, app, ticket_id, operation, **fields).status_code == 422
    assert snapshot(app, ticket_id) == before


@pytest.mark.parametrize("solution", ["", " \t\n ", "x" * 5001])
def test_solution_required_and_bounded(client, app, ticket_id, solution):
    login(client, "tecnico")
    assert save(client, app, ticket_id, "status", status="Em atendimento").status_code == 303
    before = snapshot(app, ticket_id)
    result = save(client, app, ticket_id, "status", status="Concluído", solution=solution, priority="Alta")
    assert result.status_code == 422 and snapshot(app, ticket_id) == before


def test_completion_events_and_terminal(client, app, ticket_id):
    login(client, "tecnico")
    assert save(client, app, ticket_id, "status", status="Em atendimento", actor_id=999).status_code == 303
    before = utcnow()
    assert save(client, app, ticket_id, "status", status="Concluído", solution="  <script>Correção aplicada</script>  ").status_code == 303
    state = snapshot(app, ticket_id)
    assert state[0] == "Concluído" and state[2] == "<script>Correção aplicada</script>" and before <= state[3] <= utcnow()
    with app.app_context():
        entries = db.session.scalars(db.select(StatusEvent).order_by(StatusEvent.id)).all()
        assert [(e.old_status,e.new_status) for e in entries] == [("Aberto","Em atendimento"),("Em atendimento","Concluído")]
        assert all(e.actor.role == "tecnico" and e.ticket_id == ticket_id and e.occurred_at <= utcnow() for e in entries)
    assert save(client, app, ticket_id, "prioridade", priority="Alta").status_code == 422
    assert save(client, app, ticket_id, "status", status="Em atendimento").status_code == 422
    assert snapshot(app, ticket_id) == state
    page = client.get(detail(ticket_id))
    assert "&lt;script&gt;" in page.text and "<script>" not in page.text and "Concluir chamado" not in page.text
    requester = app.test_client(); login(requester)
    assert "&lt;script&gt;" in requester.get(detail(ticket_id)).text


@pytest.mark.parametrize("operation,fields", [("prioridade", {"priority":"Alta"}), ("status", {"status":"Em atendimento"})])
def test_requester_cannot_edit(client, app, ticket_id, operation, fields):
    login(client)
    state = snapshot(app, ticket_id)
    assert save(client, app, ticket_id, operation, **fields).status_code == 403
    assert snapshot(app, ticket_id) == state


@pytest.mark.parametrize("operation", ["prioridade", "status"])
def test_edit_requires_csrf_and_version(client, app, ticket_id, operation):
    login(client, "tecnico")
    before = snapshot(app, ticket_id)
    path = f"/chamados/{ticket_id}/{operation}"
    for token in [None,"invalid"]:
        assert client.post(path, data={"csrf_token":token,"priority":"Alta","status":"Em atendimento","version":1}).status_code == 400
    assert client.post(path, data={"csrf_token":csrf(client,detail(ticket_id)),"priority":"Alta","status":"Em atendimento"}).status_code == 422
    assert snapshot(app,ticket_id) == before


def test_stale_form_rejected(client, app, ticket_id):
    login(client,"tecnico")
    token=csrf(client,detail(ticket_id))
    assert save(client,app,ticket_id,"prioridade",priority="Alta").status_code == 303
    before=snapshot(app,ticket_id)
    result=client.post(f"/chamados/{ticket_id}/status",data={"csrf_token":token,"version":1,"status":"Em atendimento"})
    assert result.status_code == 409 and snapshot(app,ticket_id) == before


@pytest.mark.parametrize("completing", [False, True])
def test_event_failure_rolls_back_status_and_solution(app,ticket_id,completing):
    with app.app_context():
        technician=db.session.scalar(db.select(User).where(User.role=="tecnico"))
        ticket=db.session.get(Ticket,ticket_id)
        if completing:
            tickets.update_status(ticket,technician,"Em atendimento","",ticket.version)
        before=(ticket.status,ticket.solution,ticket.completed_at,ticket.version,db.session.query(StatusEvent).count())
        def fail(mapper,connection,target):
            raise SQLAlchemyError("Falha simulada de evento")
        event.listen(StatusEvent,"before_insert",fail)
        try:
            with pytest.raises(SQLAlchemyError):
                tickets.update_status(ticket,technician,"Concluído" if completing else "Em atendimento",
                                      "Solução que precisa ser desfeita" if completing else "",ticket.version)
            db.session.rollback()
        finally:
            event.remove(StatusEvent,"before_insert",fail)
        db.session.remove()
        ticket=db.session.get(Ticket,ticket_id)
        assert (ticket.status,ticket.solution,ticket.completed_at,ticket.version,db.session.query(StatusEvent).count())==before


def test_concurrent_update_uses_version(app,ticket_id):
    with app.app_context():
        first=Session(db.engine); second=Session(db.engine)
        try:
            a=first.get(Ticket,ticket_id); b=second.get(Ticket,ticket_id)
            a.set_priority("Alta"); first.commit()
            b.set_priority("Baixa")
            with pytest.raises(StaleDataError): second.commit()
            second.rollback()
        finally:
            first.close();second.close()
        assert db.session.get(Ticket,ticket_id).priority=="Alta"


def test_route_rolls_back_failed_event(client,app,ticket_id):
    login(client,"tecnico")
    before=snapshot(app,ticket_id)
    def fail(mapper,connection,target):
        raise SQLAlchemyError("Falha simulada de persistência")
    event.listen(StatusEvent,"before_insert",fail)
    try:
        response=save(client,app,ticket_id,"status",status="Em atendimento")
        assert response.status_code==500
    finally:
        event.remove(StatusEvent,"before_insert",fail)
    assert snapshot(app,ticket_id)==before


def test_migration_preserves_sprint1_data(app):
    with app.app_context():
        directory=str(Path(__file__).resolve().parents[1]/"migrations")
        db.session.remove(); downgrade(directory=directory,revision="7b2f18c4a901")
        owner=db.session.scalar(db.select(User.id).where(User.role=="solicitante"))
        db.session.execute(db.text("INSERT INTO tickets(id,requester_id,title,description,category,status,opened_at) "
            "VALUES('preservar',:owner,'Chamado anterior','Descrição anterior sem alteração','Rede','Aberto',:date)"),
            {"owner":owner,"date":utcnow().isoformat(" ")})
        db.session.commit()
        rows=db.session.execute(db.text("SELECT * FROM tickets")).all()
        users=db.session.execute(db.text("SELECT * FROM users ORDER BY id")).all()
        tasks=db.session.execute(db.text("SELECT * FROM tasks ORDER BY id")).all()
        db.session.remove();upgrade(directory=directory)
        assert db.session.execute(db.text("SELECT id,requester_id,title,description,category,status,opened_at FROM tickets")).all()==rows
        assert db.session.execute(db.text("SELECT * FROM users ORDER BY id")).all()==users
        assert db.session.execute(db.text("SELECT * FROM tasks ORDER BY id")).all()==tasks
        assert db.session.get(Ticket,"preservar").priority=="Média"
        assert db.session.get(Ticket,"preservar").version==1
        assert db.session.query(StatusEvent).count()==0
