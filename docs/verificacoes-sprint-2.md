# Verificações da Sprint 2

## Aplicação e dados

- `docker compose config --quiet` passou. A imagem de testes foi construída com `docker build --target test -t helpdesk-sprint2-tests .`; `docker run --rm helpdesk-sprint2-tests` concluiu com **85 testes aprovados**, sem warnings.
- A regressão mantém login dos dois perfis, logout, proteção de rotas, abertura e confirmação privada, CSRF, escape, limites e seed idempotente. A confirmação anterior continua exclusiva do solicitante.
- Os testes da Sprint 2 verificam visibilidade e acesso direto por URL, filtros combinados nos dois perfis, paginação com ordem estável, parâmetros inválidos e repetidos, prioridades, transições, solução de 1 a 5.000 caracteres e rejeição de espaços. O técnico não abre chamados; o solicitante não altera atendimento.
- Eventos de status guardam autor, UTC e valores anterior/novo. Falhas simuladas ao inserir o evento, tanto no início quanto na conclusão, desfazem status, solução, conclusão e versão. Uma falha pela rota também retorna erro sem confirmar alteração parcial. Foram verificados formulário antigo e gravações concorrentes com sessões independentes.
- A migração foi testada sobre o esquema anterior com chamado existente. Preservou campos anteriores, usuários e tarefas, atribuiu Média e versão inicial e não inventou eventos antigos. `flask db check` não encontrou diferenças entre esquema e modelos.
- Downgrade é recusado quando há chamados em atendimento ou concluídos, pois a Sprint 1 não representa esses dados. A evolução normal aplica migrações para frente.

## Navegador e execução

Projeto Compose isolado `helpdesk-sprint2-check`, porta 8082, volume próprio. Nenhum volume existente foi apagado. O provisionamento e a migração iniciaram automaticamente, com serviço healthy.

Comando reproduzível do fluxo de navegador, usando as dependências opcionais descritas no README:

```bash
NODE_PATH=/tmp/helpdesk-browser/node_modules CHECK_COMPOSE_PROJECT=helpdesk-sprint2-check CHECK_BASE_URL=http://localhost:8082 node scripts/sprint2-check.cjs
HELPDESK_PORT=8082 docker compose -p helpdesk-sprint2-check up -d --force-recreate --wait
NODE_PATH=/tmp/helpdesk-browser/node_modules CHECK_COMPOSE_PROJECT=helpdesk-sprint2-check CHECK_BASE_URL=http://localhost:8082 node scripts/sprint2-check.cjs --verify-persistence
```

O fluxo executou abertura, confirmação, listagem, filtros, paginação, consulta dos dois perfis, prioridade, início, solução inválida, conclusão, isolamento e movimento no Kanban. Dez páginas/estados não apresentaram violações axe nos escopos A/AA executados, nem overflow horizontal em 320, 390, 768 e 1440px. Capturas em desktop/celular foram abertas e inspecionadas. Após recriação, persistiram chamado concluído, solução, prioridade, dois eventos, credenciais e coluna do quadro; a coluna de teste foi restaurada.

A análise estática de estilo não resolveu o link CSS do template Jinja e informou cores padrão nos fragmentos sem CSS. Esses avisos não correspondem ao resultado renderizado; também houve avisos sobre tamanhos anteriores já usados no sistema visual. Paleta, fontes, foco, alvos e superfícies foram preservados. Isso não certifica acessibilidade completa: não foram ensaiados leitor de tela, aparelhos físicos, Safari ou Firefox.

O primeiro ensaio encontrou filtros opcionais sem valor inicial, rejeitando a consulta sem parâmetros. Os campos passaram a ter valor vazio explícito; a regressão e o fluxo de navegador subsequentes passaram.

## Escopo preservado

A interface de histórico e o painel de indicadores não foram implementados. O Kanban continua representando tarefas do desenvolvimento. A documentação e os desenhos originais da Sprint 1 permanecem como registro histórico; as correções de modelagem são entregues na consolidação da Sprint 2.
