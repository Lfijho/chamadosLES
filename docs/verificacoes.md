# Verificações da Sprint 1

Resultados de execução real nesta implementação. Testes não usam os dados de demonstração. Containers e volumes de ensaio pertencem ao projeto isolado `helpdesk-sprint1-check`; nenhum volume foi apagado.

| Verificação | Evidência |
|---|---|
| Migração inicial em banco vazio | Alembic gerou/aplicou `3c65b6acc942`; `flask db check` não encontrou operações adicionais |
| Compose | `docker compose config --quiet` passou |
| Imagem e inicialização | Build e `docker compose -p helpdesk-sprint1-check up -d --build --wait` passaram; aplicação healthy em 127.0.0.1:8080 |
| Usuário do container | `id` retornou UID/GID 10001 (helpdesk) |
| Saúde HTTP | GET `/healthz` retornou 200 e `{"status":"ok"}` |
| Testes isolados | 43 testes passaram sem warnings, usando configuração real e banco/estado temporários |
| Falha de migração | Container descartável com revisão Alembic inválida saiu com erro; Gunicorn não foi iniciado |
| Navegador Chromium/Playwright 1.64.1 | Login dos dois perfis, abertura, confirmação, atualização GET, logout, bloqueio anônimo e movimento Kanban passaram |
| Acessibilidade automatizada | axe-core/playwright 4.11.1: nenhuma violação WCAG A/AA nos escopos executados de login, início solicitante, abertura, confirmação, início técnico e quadro |
| Responsividade | Sem overflow horizontal em 320, 390, 768 e 1440px; capturas full page em 390/1440px |
| Persistência | Após `up -d --force-recreate --wait`, mesmo chamado, sessão anterior, credenciais e coluna Kanban continuaram disponíveis; coluna original restaurada |
| Diagramas | Quatro fontes renderizadas com PlantUML 1.2025.10 em SVG/PNG; quatro PNGs abertos e inspecionados, sem cortes ou sobreposição |

## Correção encontrada durante a verificação

O navegador encontrou erro no prazo CSRF: Flask-WTF1.3.0 requer segundos nessa configuração. O valor `timedelta` foi substituído por 28.800 segundos e as fixtures passaram a carregar a configuração real, isolando apenas o diretório/banco. Depois da correção, testes e fluxo real passaram. Também foi removida a API obsoleta `get_engine()` do ambiente Alembic; execução sem warnings.

## Alcance da revisão visual

Foram inspecionadas capturas de login, páginas iniciais por perfil, formulário, confirmação e quadro, em desktop/celular. Foco do link “Pular para o conteúdo” foi verificado por teclado. Labels, alvos, estados, textos e componentes foram revisados nas capturas e nos fluxos do navegador.

O detector textual não resolve `url_for` do link CSS em Jinja, portanto avisou que a análise integrada de cores/propriedades nesse vínculo era incompleta; o arquivo CSS foi incluído diretamente na mesma execução. Contraste renderizado foi verificado pelo axe. Não há comp/QUALITY BAR externo aprovado: a revisão se refere ao brief de ferramenta interna e DESIGN.md. Não foi feita votação de alternativas visuais, conforme instrução do usuário de resolver escolhas rotineiras sem perguntas.

## Limitações e pendências reais

- Revisão de navegador em Chromium headless com viewports emulados; nenhum aparelho físico, Safari/Firefox ou leitor de tela foi usado. Não se declara certificação WCAG.
- Sem testes de carga, publicação HTTPS, recuperação de backup ou validação em outro sistema operacional. A configuração de Secure foi testada; TLS não foi implantado nesta entrega local.
- RF03–RF06 permanecem no backlog. A página do chamado apenas confirma a abertura do próprio solicitante.
- As contas e a recuperação de senhas são de demonstração local; publicação real exige ajustes descritos no README.
- CI está versionada; resultado da execução no GitHub só pode ser confirmado após push e consulta do workflow.
- Conclusão Git e verificação de clone limpo serão registradas no próximo bloco.
