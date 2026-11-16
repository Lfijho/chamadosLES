"""Restaura um backup privado somente em um diretório de estado vazio.

Uso no container auxiliar: python /restore.py /backup [/data]
"""
from contextlib import closing
import json
import os
from pathlib import Path
import sqlite3
import sys

source = Path(sys.argv[1]).resolve()
target = Path(sys.argv[2] if len(sys.argv) > 2 else "/data").resolve()
files = ("helpdesk.sqlite", "session.key", "demo-credentials.json")
if any((target / name).exists() for name in files):
    raise SystemExit("Restauração recusada: o destino já contém estado. Use um volume novo.")
if len((source / "session.key").read_text().strip()) < 32:
    raise SystemExit("Chave de sessão inválida no backup.")
credentials = json.loads((source / "demo-credentials.json").read_text())
if not credentials or not all(isinstance(k, str) and isinstance(v, str) and v for k, v in credentials.items()):
    raise SystemExit("Arquivo de credenciais inválido no backup.")
with closing(sqlite3.connect((source / "helpdesk.sqlite").as_uri() + "?mode=ro", uri=True)) as origin:
    if origin.execute("PRAGMA integrity_check").fetchone()[0] != "ok" or origin.execute("PRAGMA foreign_key_check").fetchall():
        raise SystemExit("Backup recusado pela verificação de integridade.")
    target.mkdir(mode=0o700, parents=True, exist_ok=True)
    fd = os.open(target / "helpdesk.sqlite", os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    os.close(fd)
    with closing(sqlite3.connect(target / "helpdesk.sqlite")) as destination:
        origin.backup(destination)
for name in files[1:]:
    fd = os.open(target / name, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, "wb") as stream:
        stream.write((source / name).read_bytes())
for name in files:
    os.chown(target / name, 10001, 10001)
    os.chmod(target / name, 0o600)
os.chown(target, 10001, 10001)
os.chmod(target, 0o700)
print("Backup restaurado em estado novo; arquivos privados e integridade conferidos.")
