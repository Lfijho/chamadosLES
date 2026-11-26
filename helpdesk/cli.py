import json
from contextlib import closing
import os
from pathlib import Path
import secrets
import sqlite3
import click
import yaml
from flask import current_app
from .models import COLUMNS, db, Task, User


def write_private_json(path, content):
    temporary = path.with_suffix(".tmp")
    fd = os.open(temporary, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(fd, "w") as stream:
        json.dump(content, stream, ensure_ascii=False, indent=2)
        stream.flush()
        os.fsync(stream.fileno())
    temporary.replace(path)


def seed():
    """Insere contas ausentes e sincroniza metadados sem alterar colunas/senhas."""
    state = Path(current_app.config["STATE_DIR"])
    credentials_path = state / "demo-credentials.json"
    credentials = json.loads(credentials_path.read_text()) if credentials_path.exists() else {}
    for role, name in (("solicitante", "Solicitante demonstração"), ("tecnico", "Técnico demonstração")):
        email = f"{role}@example.com"
        user = db.session.scalar(db.select(User).where(User.email == email))
        if user is None:
            # Se uma execução anterior parou antes do commit, reutiliza o segredo já salvo.
            password = credentials.get(email) or secrets.token_urlsafe(18)
            credentials[email] = password
            user = User(name=name, email=email, role=role)
            user.set_password(password)
            db.session.add(user)
    if credentials:
        # Gravar antes do commit evita contas provisionadas sem credencial recuperável.
        write_private_json(credentials_path, credentials)
    catalog = Path(current_app.root_path).parent / "docs" / "backlog.yml"
    for item in yaml.safe_load(catalog.read_text())["tasks"]:
        column = item.get("column", "Backlog")
        if column not in COLUMNS:
            raise click.ClickException("Coluna inválida no catálogo versionado.")
        task = db.session.get(Task, item["id"])
        if task is None:
            task = Task(id=item["id"], column=column)
            db.session.add(task)
        # Catálogos antigos sem descrição não apagam descrições já persistidas.
        if "description" in item:
            task.description = item["description"]
        for field in ("title", "sprint", "priority", "acceptance"):
            setattr(task, field, item[field])
    db.session.commit()


def backup_database(output):
    """Snapshot consistente do SQLite pela API de backup, sem sobrescrever arquivos."""
    if db.engine.url.get_backend_name() != "sqlite":
        raise click.ClickException("Este comando requer SQLite.")
    source = Path(db.engine.url.database).resolve()
    output = output.resolve()
    if output == source:
        raise click.ClickException("O destino não pode ser o banco em uso.")
    output.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    try:
        fd = os.open(output, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    except FileExistsError as error:
        raise click.ClickException("O destino já existe. Escolha um novo arquivo.") from error
    os.close(fd)
    try:
        with closing(sqlite3.connect(source.as_uri() + "?mode=ro", uri=True)) as origin:
            with closing(sqlite3.connect(output)) as destination:
                origin.backup(destination)
                if destination.execute("PRAGMA integrity_check").fetchone()[0] != "ok":
                    raise sqlite3.DatabaseError("Verificação de integridade recusada.")
    except (OSError, sqlite3.Error) as error:
        output.unlink(missing_ok=True)
        raise click.ClickException("Não foi possível criar uma cópia consistente do banco.") from error


def register_commands(app):
    @app.cli.command("backup-db")
    @click.argument("output", type=click.Path(path_type=Path))
    def backup_db(output):
        """Cria um snapshot consistente do SQLite no arquivo OUTPUT (privado)."""
        backup_database(output)
        click.echo("Backup consistente criado. Guarde o arquivo em local privado.")

    @app.cli.command("seed")
    def seed_command():
        """Provisiona a demonstração e sincroniza o catálogo sem redefinir estado."""
        seed()
        click.echo("Provisionamento concluído; dados existentes preservados.")

    @app.cli.command("demo-credentials")
    def demo_credentials():
        """Exibe credenciais iniciais somente por acesso local explícito ao CLI."""
        path = Path(current_app.config["STATE_DIR"]) / "demo-credentials.json"
        if not path.exists():
            raise click.ClickException("Credenciais indisponíveis. Execute as migrações e o seed.")
        for email, password in json.loads(path.read_text()).items():
            click.echo(f"E-mail: {email}\nSenha: {password}\n")
