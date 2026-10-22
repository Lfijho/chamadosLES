# HelpDesk — Sistema de Controle de Chamados de TI

Projeto de Laboratório de Engenharia de Software, desenvolvido individualmente por **Leandro Pinzon Filho**. Entrega da Sprint 1: **29/10/2026**.

A Sprint 1 implementa RF01 (autenticação) e RF02 (abertura de chamado). Solicitantes abrem chamados e recebem uma confirmação privada com protocolo; técnicos acessam uma página inicial e o quadro auxiliar do desenvolvimento. Consulta com filtros e atendimento (Sprint 2), histórico e indicadores (Sprint 3) permanecem no backlog.

## Iniciar

Pré-requisitos no host: Docker Engine e Docker Compose com suporte a `compose.yml`. Na raiz de um clone:

```bash
docker compose up -d
```

Acesse **http://localhost:8080**. A primeira construção baixa a imagem e as dependências. O container prepara automaticamente o volume, gera a chave, aplica migrações, provisiona as contas e sincroniza o catálogo. Não é necessário instalar Python/Node, criar `.env` ou editar arquivos no host.

```bash
docker compose ps
docker compose exec app flask demo-credentials
```

O segundo comando mostra localmente os e-mails e as senhas aleatórias iniciais de `solicitante@example.com` e `tecnico@example.com`. Credenciais não são versionadas nem escritas nos logs. Quem tem acesso ao Docker pode ler os segredos do volume; restrinja esse acesso. Não cole a saída em issues ou commits.

## Persistência e operação

O volume nomeado `<projeto-compose>_helpdesk_state` contém SQLite, chave de sessão e credenciais iniciais. Permissões são preparadas pela imagem; a aplicação e o provisionamento executam como UID/GID 10001. O seed não redefine senhas, não duplica contas/tarefas nem altera colunas existentes do quadro. Metadados de tarefas são sincronizados de `docs/backlog.yml`.

```bash
docker compose logs --tail 50 app
docker compose up -d --force-recreate --wait
docker compose down
docker compose up -d
```

Esses comandos preservam os dados. Não use `down -v` ou remova o volume se deseja preservá-los. Mudanças no código exigem `docker compose up -d --build`. A política `unless-stopped` reinicia o processo se ele falhar; migrações com erro encerram a inicialização sem iniciar o servidor.

A porta é publicada somente em `127.0.0.1`. Para trocar a porta sem editar arquivos: `HELPDESK_PORT=8081 docker compose up -d`. `/healthz` responde 200 quando consegue consultar a revisão de migração e tabelas do banco; caso contrário responde 503. Logs operacionais vão a stdout/stderr sem corpo de formulários, senha, cookie ou query string. O servidor é Gunicorn, sem debug, um worker e quatro threads; `exec` e o init do Docker encaminham os sinais de encerramento.

## Testes

Banco e estado são temporários em cada teste; o container de testes não monta o volume de demonstração:

```bash
docker build --target test -t helpdesk-tests .
docker run --rm helpdesk-tests
docker compose config --quiet
```

Alternativa para desenvolvimento, com Python 3.13 e ambiente virtual já disponível: `pip install -r requirements-dev.lock` e `python -m pytest -q`. O teste usa a configuração real e troca o diretório de estado por um temporário. Não execute testes sobre o banco de demonstração.

O workflow `.github/workflows/ci.yml` executa a suíte, valida o Compose e testa a inicialização/saúde. O resultado local e as limitações estão em [docs/verificacoes.md](docs/verificacoes.md).

A verificação opcional de navegador/persistência usa dados sintéticos e um projeto isolado. Requer Node apenas para essa verificação, nunca para iniciar a aplicação:

```bash
npm install --prefix /tmp/helpdesk-browser playwright@1.64.1 @axe-core/playwright@4.11.1
NODE_PATH=/tmp/helpdesk-browser/node_modules /tmp/helpdesk-browser/node_modules/.bin/playwright install chromium
HELPDESK_PORT=8081 docker compose -p helpdesk-browser-check up -d --build --wait
NODE_PATH=/tmp/helpdesk-browser/node_modules CHECK_COMPOSE_PROJECT=helpdesk-browser-check CHECK_BASE_URL=http://localhost:8081 node scripts/browser-check.cjs
HELPDESK_PORT=8081 docker compose -p helpdesk-browser-check up -d --force-recreate --wait
NODE_PATH=/tmp/helpdesk-browser/node_modules CHECK_COMPOSE_PROJECT=helpdesk-browser-check CHECK_BASE_URL=http://localhost:8081 node scripts/browser-check.cjs --verify-persistence
HELPDESK_PORT=8081 docker compose -p helpdesk-browser-check down
```

Capturas locais ficam em `artifacts/browser/`, ignoradas no Git. O estado temporário do teste de navegador contém um cookie de teste em `/tmp/helpdesk-browser-check-state.json`, com modo 0600; remova-o após verificar. Nenhum volume é apagado.

## Diagramas e documentação

PlantUML substitui o diagrams.net inicialmente previsto para permitir fontes versionadas e renderização reproduzível. Não havia arquivo existente exigindo `.drawio`. Os quatro desenhos em SVG e PNG já estão entregues; o renderizador é opcional e independente da aplicação:

```bash
./scripts/render-diagrams.sh
```

O script usa `plantuml/plantuml:1.2025.10`, profile `tools`, sem rede no container e com UID/GID do usuário para escrever os desenhos. Em ambientes sem shell POSIX, execute os comandos `docker compose --profile tools run --rm --no-deps diagrams -charset UTF-8 -tsvg '*.puml'` e a variante `-tpng`, ajustando DIAGRAM_UID/DIAGRAM_GID conforme o host.

- [Documentação acadêmica, requisitos, casos de uso e diagramas](docs/sprint-1.md).
- [Catálogo inicial de tarefas e critérios](docs/backlog.yml).
- [Acompanhamento versionado](docs/kanban.md): registro do código verificado. O quadro da aplicação mantém o estado operacional no banco, exclusivo do técnico.
- [Registro das verificações e limites reais](docs/verificacoes.md).
- [Contexto do produto](PRODUCT.md) e [sistema visual](DESIGN.md).

## Arquitetura e evolução

`helpdesk/__init__.py` cria a aplicação, registra extensões, rotas, erros e cabeçalhos. `config.py` configura o estado e os cookies; `models.py` define persistência e invariantes; `forms.py` valida entrada; `security.py` centraliza permissões, sessões e limites; `routes.py` implementa os fluxos; `cli.py` provisiona. Templates Jinja2 escapam conteúdo; CSS local não depende de CDN. Migrações em `migrations/`, testes em `tests/`.

Datas no SQLite são armazenadas sem offset e representam UTC; a interface identifica UTC explicitamente. Protocolo usa UUID v4 completo com prefixo HD-. A confirmação é acessível somente ao autor autenticado e não substitui a listagem futura.

Para futuras alterações de esquema, gere uma nova revisão com Flask-Migrate e revise-a antes de aplicar; não modifique a revisão já entregue. O status de chamado está restrito a Aberto nesta Sprint; RF04 exigirá migração para ampliar essa regra. O catálogo do Kanban aceita novos IDs e atualizações de metadados, preservando colunas e tarefas adicionais.

## Configuração local de demonstração e publicação real

Esta entrega é configurada para demonstração local em HTTP. Cookies têm HttpOnly, SameSite=Lax e prazo de 8 horas; `Secure=false` permite localhost HTTP. A sessão autenticada tem limite absoluto de 8 horas validado no banco e é revogada no logout. CSRF protege todos os POSTs. Limites persistem por 10 minutos: cinco falhas por conta e trinta por IP; contas desconhecidas recebem a mesma mensagem e verificação contra hash fictício. Contadores usam HMAC e não guardam e-mail/IP em claro. É uma mitigação básica para uma instância, sem serviço externo de limitação.

Para HTTPS, termine TLS em proxy controlado, configure `COOKIE_SECURE=true` e recrie o container. Ative HSTS no proxy somente após confirmar HTTPS. Se publicar atrás de proxy, configure e teste explicitamente a confiança no encaminhamento de IP; a aplicação hoje usa o IP direto, sem confiar em `X-Forwarded-For`. Publique somente pelas rotas e interfaces necessárias.

Antes de publicar fora da demonstração: desabilite/substitua o provisionamento automático de contas demo e a recuperação de suas senhas; use gestão de segredos e contas institucionais, política de senha, backups consistentes do SQLite e testes de restauração, monitoramento, TLS, atualização de dependências e revisão de acesso/privacidade. Não exponha as contas de demonstração na internet. O arquivo de credenciais contém senhas iniciais em claro exclusivamente para recuperação local solicitada; senhas de autenticação são verificadas por hash scrypt no banco.

Uma chave externa pode ser fornecida como `SECRET_KEY` (mínimo 32 caracteres aleatórios) ao ambiente do serviço por um override privado/gestor de segredos. Sem ela, a chave é gerada com `secrets` e preservada no volume em modo 0600. Nunca versione esse valor. Trocar a chave invalida cookies existentes.

## Roteiro de demonstração

1. Execute `docker compose up -d`, mostre o estado healthy e recupere credenciais no terminal local.
2. Como solicitante, tente senha incorreta, entre e abra um chamado da categoria Rede. Mostre a validação obrigatória de campos.
3. Envie dados válidos. Mostre protocolo, autor implícito, status Aberto e abertura UTC. Atualize a confirmação para comprovar PRG.
4. Saia e mostre que a URL privada exige login.
5. Entre como técnico. Mostre a mensagem de escopo e o quadro acadêmico; mova uma tarefa pelo seletor.
6. Recrie os containers sem apagar volumes e confirme que o quadro persiste.
7. Apresente os testes, os desenhos UML e os itens futuros no backlog, sem alegar implantação de RF03–RF06.
