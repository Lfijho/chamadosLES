# HelpDesk

Aplicação web de controle de chamados de TI em Flask, HTML/CSS e SQLite. Permite autenticação, abertura e consulta de chamados, atendimento com prioridade/status/solução, histórico com anotações e indicadores. Solicitantes consultam os próprios chamados; técnicos conduzem o atendimento. O Kanban auxiliar acompanha as tarefas de desenvolvimento.

## Executar

Requer Docker e Docker Compose. Na raiz do repositório:

```bash
docker compose up -d
```

Acesse **http://localhost:8080**. Após atualizar o código de uma instalação com imagem já construída, execute `docker compose up -d --build`.

Consulte as credenciais iniciais de demonstração somente no terminal local:

```bash
docker compose exec app flask demo-credentials
```

As senhas são geradas no primeiro provisionamento. Não publique a saída desse comando. A configuração é destinada à demonstração local; as contas não devem ser expostas na internet.

## Estado e configuração

O volume nomeado `helpdesk_state` preserva o banco, a chave de sessão e as credenciais. Não remova o volume nem use `docker compose down -v` se deseja manter os dados. A inicialização aplica migrações e provisionamento idempotente. `docs/backlog.yml` é o catálogo utilizado pelo Kanban; a sincronização preserva as colunas alteradas pelo usuário.

```bash
docker compose ps
docker compose logs --tail 50 app
docker compose down
```

A porta é publicada em localhost. Use `HELPDESK_PORT=8081 docker compose up -d` para selecionar outra porta. O serviço usa Gunicorn e disponibiliza `/healthz` para conferir aplicação e banco. Em HTTPS, configure `COOKIE_SECURE=true`; o padrão local permite HTTP.

## Testar

Os testes usam banco temporário, sem montar o volume da aplicação:

```bash
docker compose config --quiet
docker build --target test -t helpdesk-tests .
docker run --rm helpdesk-tests
```

Configuração em `helpdesk/`, migrações em `migrations/` e testes em `tests/`. Scripts de verificação e manutenção ficam em `scripts/`.
