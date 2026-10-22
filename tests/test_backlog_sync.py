"""Verifica catálogo futuro sem implementar RF03–RF06."""
from pathlib import Path
import yaml
from flask_migrate import downgrade, upgrade
from helpdesk.cli import seed
from helpdesk.models import db, Task, Ticket, User
from conftest import login

S2_NEW = {f"S2-{number:02}" for number in range(4, 13)}
S3_NEW = {f"S3-{number:02}" for number in range(4, 14)}
NEW_IDS = S2_NEW | S3_NEW


def catalog():
    return yaml.safe_load((Path(__file__).resolve().parents[1] / "docs/backlog.yml").read_text())


def test_future_catalog_has_complete_metadata_and_backlog():
    content = catalog()
    tasks = content["tasks"]
    assert len({task["id"] for task in tasks}) == len(tasks) == 33
    assert content["sprints"][2]["delivery"] == "2026-11-12"
    assert content["sprints"][3]["delivery"] == "2026-12-03"
    detailed = {task["id"]: task for task in tasks if task["id"] in NEW_IDS}
    assert set(detailed) == NEW_IDS
    medium = {"S2-12", "S3-11", "S3-13"}
    for task_id, task in detailed.items():
        assert task["column"] == "Backlog"
        assert task["sprint"] == int(task_id[1])
        assert task["title"].strip() and len(task["title"]) <= 160
        assert task["description"].strip() and task["acceptance"].strip()
        assert task["priority"] == ("Média" if task_id in medium else "Alta")


def test_two_imports_add_only_missing_tasks_and_preserve_existing_data(app):
    with app.app_context():
        # Recria a situação anterior ao novo catálogo somente no banco temporário.
        db.session.execute(db.delete(Task).where(Task.id.in_(NEW_IDS)))
        db.session.get(Task, "S1-01").column = "A fazer"
        db.session.get(Task, "S2-01").column = "Em andamento"
        db.session.get(Task, "S3-01").column = "A fazer"
        db.session.get(Task, "S1-02").description = "Descrição local de catálogo antigo"
        db.session.add(Task(id="LOCAL", title="Tarefa local", sprint=1, priority="Média",
                            description="Não apagar", acceptance="Preservar", column="Em andamento"))
        user_id = db.session.scalar(db.select(User.id).where(User.email == "solicitante@example.com"))
        db.session.add(Ticket(requester_id=user_id, title="Chamado anterior", description="Preservar dados antigos.", category="Rede"))
        db.session.commit()
        users = {user.id: (user.email, user.password_hash, user.role) for user in db.session.scalars(db.select(User))}
        s1 = {task.id: (task.title, task.sprint, task.priority, task.acceptance, task.description, task.column)
              for task in db.session.scalars(db.select(Task).where(Task.sprint == 1))}
        columns = {task.id: task.column for task in db.session.scalars(db.select(Task))}
        ticket_id = db.session.scalar(db.select(Ticket.id))
        credentials = (app.config["STATE_DIR"] / "demo-credentials.json").read_bytes()
        for _ in range(2):
            seed()
            db.session.remove()
            tasks = db.session.scalars(db.select(Task)).all()
            assert len(tasks) == 34  # 33 do catálogo e uma tarefa local preservada.
            assert {task.id: task.column for task in tasks if task.id in columns} == columns
            assert {task.id for task in tasks if task.id not in columns} == NEW_IDS
            assert all(task.column == "Backlog" and task.description for task in tasks if task.id in NEW_IDS)
            assert {task.id: (task.title, task.sprint, task.priority, task.acceptance, task.description, task.column)
                    for task in tasks if task.sprint == 1} == s1
            assert {user.id: (user.email, user.password_hash, user.role)
                    for user in db.session.scalars(db.select(User))} == users
            assert db.session.query(Ticket).count() == 1
            assert db.session.get(Ticket, ticket_id).title == "Chamado anterior"
            assert (app.config["STATE_DIR"] / "demo-credentials.json").read_bytes() == credentials


def test_description_migration_preserves_old_rows(app):
    with app.app_context():
        migrations = str(Path(__file__).resolve().parents[1] / "migrations")
        db.session.remove()
        downgrade(directory=migrations, revision="3c65b6acc942")
        before = db.session.execute(db.text('SELECT id,title,sprint,priority,acceptance,"column" FROM tasks ORDER BY id')).all()
        db.session.remove()
        upgrade(directory=migrations)
        after = db.session.execute(db.text('SELECT id,title,sprint,priority,acceptance,"column" FROM tasks ORDER BY id')).all()
        assert after == before
        assert all(description == "" for description in db.session.scalars(db.select(Task.description)))


def test_kanban_displays_descriptions_escaped(client, app):
    login(client, "tecnico")
    page = client.get("/kanban")
    assert page.status_code == 200
    assert "S2-12" in page.text and "S3-13" in page.text
    assert "Concluído será terminal nesta entrega." in page.text
    assert "Não inventar eventos antigos ausentes no banco" in page.text
    with app.app_context():
        db.session.get(Task, "S2-04").description = "<script>alert('x')</script>"
        db.session.commit()
    assert "&lt;script&gt;" in client.get("/kanban").text
