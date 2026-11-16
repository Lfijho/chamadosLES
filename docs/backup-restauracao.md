# Backup e restauração local

O SQLite contém chamados e dados pessoais; a chave e o arquivo de demonstração também são privados. Use uma pasta ignorada pelo Git e proteja qualquer cópia externa. Não envie esses arquivos ao LEX ou ao repositório.

## Criar a cópia

Interrompa no primeiro erro e avance somente após o sucesso de cada comando.

```bash
mkdir -p runtime/backup
chmod 700 runtime runtime/backup
docker compose exec app flask backup-db /data/backups/entrega.sqlite
docker compose cp app:/data/backups/entrega.sqlite runtime/backup/helpdesk.sqlite
docker compose stop app
docker compose cp app:/data/session.key runtime/backup/session.key
docker compose cp app:/data/demo-credentials.json runtime/backup/demo-credentials.json
docker compose start app
chmod 600 runtime/backup/*
```

Escolha outro nome de snapshot se `entrega.sqlite` já existir: o comando recusa sobrescrita. `backup-db` usa a API de backup do SQLite e verifica integridade, podendo ler o banco com a aplicação ativa. Não use `cp` no arquivo SQLite em uso. A breve parada dos comandos acima permite guardar os arquivos auxiliares sem provisionamento concorrente; retome a aplicação após copiá-los. O snapshot do banco corresponde ao momento do backup, não a alterações posteriores.

## Restaurar em projeto e volume novos

O procedimento abaixo preserva a instância original e não publica a porta de restauração em toda a rede. Requer uma cópia de `helpdesk.sqlite`, `session.key` e `demo-credentials.json` em `runtime/backup`.

```bash
HELPDESK_PORT=8086 docker compose -p helpdesk-restore-check build app &&
HELPDESK_PORT=8086 docker compose -p helpdesk-restore-check run --rm --no-deps --user 0:0 --cap-add DAC_OVERRIDE --cap-add CHOWN --cap-add FOWNER --entrypoint python -v "$PWD/runtime/backup:/backup:ro" -v "$PWD/scripts/restore-backup.py:/restore.py:ro" app /restore.py /backup &&
HELPDESK_PORT=8086 docker compose -p helpdesk-restore-check up -d --wait
```

Abra `http://localhost:8086`, confira o healthcheck, autentique-se e consulte os chamados. Migrações posteriores são aplicadas pela inicialização normal. O auxiliar de restauração recusa destino que já contenha estado, valida integridade e chaves estrangeiras e ajusta os arquivos para o usuário da aplicação. O processo normal continua sem privilégios de root; o auxiliar usa root e três capacidades de arquivos apenas para preparar o volume novo e suas permissões. Elas são necessárias porque o serviço normal remove todas as capacidades.

Para encerrar o ensaio, execute `docker compose -p helpdesk-restore-check down`, sem `-v`. Não remova volumes de uso nem copie arquivos por cima de um banco ativo. Uma recuperação da instância original deve ser planejada a partir da cópia já verificada; este procedimento não a substitui nem sobrescreve.
