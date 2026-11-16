"""Histórico e indicadores com estado temporário e migração de dados anteriores."""
from datetime import timedelta
from pathlib import Path
import pytest
from flask_migrate import downgrade, upgrade
from sqlalchemy import event
from sqlalchemy.exc import SQLAlchemyError
from werkzeug.exceptions import Forbidden, NotFound
from helpdesk.models import db, Ticket, TicketNote, StatusEvent, User, utcnow
from helpdesk import tickets
from conftest import csrf, login


@pytest.fixture()
def ticket_id(app):
    with app.app_context():
        owner = db.session.scalar(db.select(User).where(User.role == "solicitante"))
        ticket = Ticket(requester_id=owner.id, title="Falha de rede no laboratório", category="Rede",
                        description="Não é possível acessar a rede do laboratório.")
        db.session.add(ticket)
        db.session.commit()
        return ticket.id


def detail(ticket_id):
    return f"/chamados/{ticket_id}/detalhes"


def add(client, ticket_id, content, **extra):
    return client.post(f"/chamados/{ticket_id}/anotacoes", data={
        "csrf_token": csrf(client, detail(ticket_id)), "content": content, **extra})


def ticket_state(ticket):
    return ticket.status, ticket.priority, ticket.solution, ticket.completed_at, ticket.version


@pytest.mark.parametrize("content", ["x", "x" * 5000, "漢" * 5000, "  Conferida a conexão. \n"])
def test_note_author_utc_and_prg(client, app, ticket_id, content):
    login(client, "tecnico")
    with app.app_context():
        before = ticket_state(db.session.get(Ticket, ticket_id))
        start = utcnow()
    response = add(client, ticket_id, content, author_id=999, requester_id=999,
                   status="Concluído", priority="Alta", solution="Não deve ser gravada.")
    assert response.status_code == 303 and response.location.endswith("#historico")
    page = client.get(response.location)
    assert page.status_code == 200 and content.strip() in page.text
    client.get(response.location)  # Atualizar a página não reenvia a anotação.
    with app.app_context():
        note = db.session.scalar(db.select(TicketNote))
        assert note.content == content.strip() and note.ticket_id == ticket_id
        assert note.author.role == "tecnico" and note.author.email == "tecnico@example.com"
        assert start <= note.occurred_at <= utcnow() and note.occurred_at.tzinfo is None
        assert db.session.query(TicketNote).count() == 1
        assert ticket_state(db.session.get(Ticket, ticket_id)) == before
        assert db.session.query(StatusEvent).count() == 0


@pytest.mark.parametrize("content", ["", " ", "\n\t\u2003", "x" * 5001])
def test_invalid_note_rejected(client, app, ticket_id, content):
    login(client, "tecnico")
    response = add(client, ticket_id, content)
    assert response.status_code == 422 and "A alteração não foi salva" in response.text
    with app.app_context():
        assert db.session.query(TicketNote).count() == 0


def test_note_escape_and_requester_read_only(client, app, ticket_id):
    login(client, "tecnico")
    assert add(client, ticket_id, '<script>alert("x")</script>\nConexão verificada.').status_code == 303
    page = client.get(detail(ticket_id))
    assert "&lt;script&gt;" in page.text and "<script>" not in page.text
    import re
    assert re.search(r"<title>(.*?)</title>",page.text,re.S).group(1)=="Detalhes do chamado · Suporte de TI"
    assert page.text.count('id="historico"')==1
    owner = app.test_client(); login(owner)
    page = owner.get(detail(ticket_id))
    assert "&lt;script&gt;" in page.text and "Conexão verificada." in page.text
    assert "Adicionar anotação" not in page.text
    assert add(owner, ticket_id, "Tentativa indevida").status_code == 403
    other = app.test_client(); login(other, email="outra@example.com")
    assert other.get(detail(ticket_id) + "?author_id=1").status_code == 404
    assert other.post(f"/chamados/{ticket_id}/anotacoes", data={
        "csrf_token": csrf(other, "/"), "content": "Tentativa indevida"}).status_code == 403
    with app.app_context():
        assert db.session.query(TicketNote).count() == 1


def test_notes_require_auth_csrf_and_existing_ticket(client, app, ticket_id):
    anonymous = app.test_client()
    # A proteção global rejeita POST sem CSRF antes de avaliar a autenticação.
    assert anonymous.post(f"/chamados/{ticket_id}/anotacoes", data={"content":"teste"}).status_code == 400
    assert anonymous.post(f"/chamados/{ticket_id}/anotacoes", data={
        "content":"teste", "csrf_token":csrf(anonymous,"/login")}).status_code == 302
    login(client,"tecnico")
    for token in [None,"inválido"]:
        assert client.post(f"/chamados/{ticket_id}/anotacoes", data={"content":"teste","csrf_token":token}).status_code == 400
    assert client.post("/chamados/00000000-0000-0000-0000-000000000000/anotacoes", data={
        "csrf_token":csrf(client,"/"),"content":"teste"}).status_code == 404
    assert client.get(f"/chamados/{ticket_id}/anotacoes").status_code == 405


def test_empty_history_and_no_fabricated_opening(client, app, ticket_id):
    login(client)
    page = client.get(detail(ticket_id))
    assert "Ainda não há registros de atendimento" in page.text
    with app.app_context():
        ticket = db.session.get(Ticket,ticket_id)
        owner = db.session.get(User,ticket.requester_id)
        assert tickets.get_history(ticket,owner) == []


def test_history_chronology_stable_ties_and_isolation(client, app, ticket_id):
    with app.app_context():
        ticket = db.session.get(Ticket,ticket_id)
        tech = db.session.scalar(db.select(User).where(User.role=="tecnico"))
        tickets.update_status(ticket,tech,"Em atendimento","",ticket.version)
        tickets.update_status(ticket,tech,"Concluído","Rede restabelecida.",ticket.version)
        events = db.session.scalars(db.select(StatusEvent).order_by(StatusEvent.id)).all()
        moment = utcnow()
        # Inserção fora de ordem cronológica e empate entre tipos e dentro do mesmo tipo.
        events[0].occurred_at = moment
        events[1].occurred_at = moment
        notes = [TicketNote(ticket=ticket,author=tech,content=text,occurred_at=at) for text,at in [
            ("Nota posterior",moment+timedelta(seconds=1)),("Nota no empate 1",moment),
            ("Nota anterior",moment-timedelta(seconds=1)),("Nota no empate 2",moment)]]
        db.session.add_all(notes)
        other = db.session.scalar(db.select(User).where(User.email=="outra@example.com"))
        private = Ticket(requester_id=other.id,title="Chamado de outra pessoa",category="Outros",description="Descrição privada de outro chamado.")
        db.session.add(private); db.session.flush()
        db.session.add(TicketNote(ticket=private,author=tech,content="Segredo de outro chamado"))
        db.session.commit()
        owner = db.session.get(User,ticket.requester_id)
        entries = tickets.get_history(ticket,owner)
        expected = ["Nota anterior", "Em atendimento", "Concluído", "Nota no empate 1", "Nota no empate 2", "Nota posterior"]
        assert [e["content"] if e["kind"]=="note" else e["new_status"] for e in entries] == expected
        assert all(e["author"]==tech.name for e in entries)
        assert tickets.get_history(ticket,tech)==entries
        with pytest.raises(NotFound): tickets.get_history(ticket,other)
        assert tickets.get_history(ticket,owner)==entries
    login(client)
    assert "Segredo de outro chamado" not in client.get(detail(ticket_id)).text


def test_note_after_completion_does_not_reopen(client, app, ticket_id):
    with app.app_context():
        ticket=db.session.get(Ticket,ticket_id)
        tech=db.session.scalar(db.select(User).where(User.role=="tecnico"))
        tickets.update_status(ticket,tech,"Em atendimento","",ticket.version)
        tickets.update_status(ticket,tech,"Concluído","Correção aplicada.",ticket.version)
        before=ticket_state(ticket)
    login(client,"tecnico")
    assert add(client,ticket_id,"Observação após a conclusão.",status="Aberto",priority="Alta").status_code==303
    with app.app_context():
        assert ticket_state(db.session.get(Ticket,ticket_id))==before
        assert db.session.query(StatusEvent).count()==2
        note=db.session.scalar(db.select(TicketNote))
        token=csrf(client,detail(ticket_id))
        for method in (client.put,client.patch,client.delete):
            assert method(f"/chamados/{ticket_id}/anotacoes/{note.id}",data={"csrf_token":token}).status_code==404
        assert db.session.query(TicketNote).count()==1


def test_services_enforce_permissions_and_note_limit(app,ticket_id):
    with app.app_context():
        t=db.session.get(Ticket,ticket_id); owner=db.session.get(User,t.requester_id)
        tech=db.session.scalar(db.select(User).where(User.role=="tecnico"))
        with pytest.raises(Forbidden): tickets.add_note(t,owner,"Não autorizado")
        with pytest.raises(Forbidden): tickets.get_indicators(owner)
        for content in [None," \u2003", "x"*5001]:
            with pytest.raises(ValueError): tickets.add_note(t,tech,content)
        assert db.session.query(TicketNote).count()==0


def test_note_failure_rolls_back(client,app,ticket_id):
    login(client,"tecnico")
    with app.app_context(): before=ticket_state(db.session.get(Ticket,ticket_id))
    def fail(*args): raise SQLAlchemyError("Falha simulada de persistência")
    event.listen(TicketNote,"before_insert",fail)
    try: assert add(client,ticket_id,"Não deve persistir.").status_code==500
    finally: event.remove(TicketNote,"before_insert",fail)
    with app.app_context():
        assert db.session.query(TicketNote).count()==0
        assert ticket_state(db.session.get(Ticket,ticket_id))==before


def test_indicators_permissions_and_zero(client, app):
    assert client.get("/indicadores").status_code==302
    login(client)
    assert client.get("/indicadores").status_code==403
    assert "Indicadores</a>" not in client.get("/").text
    client.post("/logout",data={"csrf_token":csrf(client,"/")})
    login(client,"tecnico")
    page=client.get("/indicadores")
    assert page.status_code==200 and page.text.count("<td>0</td>")==6
    with app.app_context():
        tech=db.session.scalar(db.select(User).where(User.role=="tecnico"))
        assert tickets.get_indicators(tech)=={"status":{"Aberto":0,"Em atendimento":0,"Concluído":0},
                                             "priority":{"Baixa":0,"Média":0,"Alta":0}}


def test_indicators_follow_changes_and_ignore_history(client,app):
    login(client,"tecnico")
    def counts():
        with app.app_context():
            tech=db.session.scalar(db.select(User).where(User.role=="tecnico"))
            return tickets.get_indicators(tech)
    with app.app_context():
        owner=db.session.scalar(db.select(User).where(User.role=="solicitante"))
        tech=db.session.scalar(db.select(User).where(User.role=="tecnico"))
        a=tickets.create_ticket(owner,"Falha de acesso","Descrição do problema.","Acessos")
        b=tickets.create_ticket(owner,"Problema em software","Descrição do segundo problema.","Software")
        aid=a.id
    assert counts()["status"]["Aberto"]==2 and counts()["priority"]["Média"]==2
    with app.app_context():
        a=db.session.get(Ticket,aid);tech=db.session.scalar(db.select(User).where(User.role=="tecnico"))
        tickets.update_priority(a,tech,"Alta",a.version)
        tickets.update_status(a,tech,"Em atendimento","",a.version)
        for i in range(3): tickets.add_note(a,tech,f"Registro {i}")
    assert counts()=={"status":{"Aberto":1,"Em atendimento":1,"Concluído":0},"priority":{"Baixa":0,"Média":1,"Alta":1}}
    with app.app_context():
        a=db.session.get(Ticket,aid);tech=db.session.scalar(db.select(User).where(User.role=="tecnico"))
        tickets.update_status(a,tech,"Concluído","Correção concluída.",a.version)
        tickets.add_note(a,tech,"Observação final.")
    expected={"status":{"Aberto":1,"Em atendimento":0,"Concluído":1},"priority":{"Baixa":0,"Média":1,"Alta":1}}
    assert counts()==expected
    page=client.get("/indicadores")
    assert page.status_code==200 and page.text.count("<td>1</td>")==4


def test_migration_preserves_sprint2_rows_and_events(app):
    with app.app_context():
        directory=str(Path(__file__).resolve().parents[1]/"migrations")
        db.session.remove();downgrade(directory=directory,revision="ab92105d63e0")
        owner=db.session.scalar(db.select(User.id).where(User.role=="solicitante"))
        tech=db.session.scalar(db.select(User.id).where(User.role=="tecnico"))
        now=utcnow()
        db.session.execute(db.text("INSERT INTO tickets(id,requester_id,title,description,category,status,opened_at,priority,version) "
            "VALUES('sprint2-preservado',:owner,'Chamado da Sprint 2','Conteúdo anterior preservado.','Rede','Em atendimento',:now,'Alta',2)"),{"owner":owner,"now":now.isoformat(" ")})
        db.session.execute(db.text("INSERT INTO status_events(ticket_id,actor_id,occurred_at,old_status,new_status) "
            "VALUES('sprint2-preservado',:tech,:now,'Aberto','Em atendimento')"),{"tech":tech,"now":now.isoformat(" ")})
        db.session.commit()
        tables=["tickets","status_events","users","tasks"]
        before={name:db.session.execute(db.text(f"SELECT * FROM {name} ORDER BY id")).all() for name in tables}
        db.session.remove();upgrade(directory=directory)
        for name in tables: assert db.session.execute(db.text(f"SELECT * FROM {name} ORDER BY id")).all()==before[name]
        t=db.session.get(Ticket,"sprint2-preservado");user=db.session.get(User,owner)
        history=tickets.get_history(t,user)
        assert len(history)==1 and history[0]["old_status"]=="Aberto" and history[0]["author"]=="Técnico demonstração"
        assert db.session.query(TicketNote).count()==0


def test_sqlite_backup_and_restore_snapshot(app, ticket_id, tmp_path):
    import sqlite3
    from helpdesk.cli import backup_database
    import click
    with app.app_context():
        ticket=db.session.get(Ticket,ticket_id)
        tech=db.session.scalar(db.select(User).where(User.role=="tecnico"))
        tickets.update_status(ticket,tech,"Em atendimento","",ticket.version)
        tickets.add_note(ticket,tech,"Registro que deve sobreviver ao backup.")
        target=tmp_path/"backups"/"snapshot.sqlite"
        backup_database(target)
        assert target.stat().st_mode & 0o777==0o600
        with pytest.raises(click.ClickException): backup_database(target)
        with pytest.raises(click.ClickException): backup_database(Path(db.engine.url.database))
        # A restauração ocorre em um arquivo novo e isolado; a origem segue intacta.
        restored=tmp_path/"restaurado.sqlite"
        with sqlite3.connect(target) as saved, sqlite3.connect(restored) as dest:
            saved.backup(dest)
            assert dest.execute("PRAGMA integrity_check").fetchone()[0]=="ok"
            assert dest.execute("PRAGMA foreign_key_check").fetchall()==[]
            for name in ["tickets","status_events","ticket_notes","users","tasks","alembic_version"]:
                assert dest.execute(f"SELECT * FROM {name}").fetchall()==db.session.execute(db.text(f"SELECT * FROM {name}")).fetchall()
        assert db.session.query(TicketNote).count()==1
