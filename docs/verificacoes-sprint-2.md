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


## Consolidação e conferência UML

| Requisito | Casos de uso | Operações e objetos principais |
|---|---|---|
| RF01 | UC01, UC02 | login, authenticate, User.check_password, start_session, logout |
| RF02 | UC03 | new_ticket, create_ticket, ticket_confirmation, get_ticket, Ticket |
| RF03 | UC04, UC05 | ticket_list, visible_tickets, list_tickets, ticket_detail, ticket_detail_response |
| RF04 | UC06, UC07 | ticket_priority, ticket_status, check_edit, update_priority, update_status, Ticket.set_priority, Ticket.change_status, StatusEvent |

A conferência comparou nomes das tabelas com as definições do código e as mensagens de cada sequência. Foram revisados atores externos tradicionais, limite HelpDesk, associações diretas e separação do Kanban. As sequências usam módulos Flask e objetos reais, retornos tracejados, ativações e condições; a persistência não é tratada como entidade de domínio. As associações de Ticket e StatusEvent identificam solicitante, chamado e autor, com multiplicidades. As funções de módulo permanecem como funções. No diagrama de atividades, o HelpDesk valida os dados; solicitante e técnico fazem as correções indicadas.

As dez fontes foram renderizadas em SVG e PNG. A revisão visual encontrou e corrigiu recorte de uma imagem e dimensionamento indevido no exportador. O renderizador opcional passou a aceitar imagens maiores, e o exportador aplica os limites declarados na fonte após definir a orientação das páginas. As 15 páginas finais foram abertas: oito usam paisagem; tabelas, legendas, imagens e numeração foram conferidas. A verificação do DOCX encontrou nove tabelas nativas e dez imagens com conteúdo igual aos PNGs referenciados no Markdown. A geração isolada da Sprint 1 continuou produzindo seis páginas, sem alterar os arquivos históricos do repositório.

A prosa final foi revisada preservando requisitos, nomes, comandos e fatos. DOCX foi exportado pelo LibreOffice; não houve inspeção no Microsoft Word. A avaliação e a aceitação pelo professor continuam pendentes.

## Inicialização limpa e atualização do volume existente

Uma exportação Git sem arquivos locais ou runtime iniciou pelo comando `docker compose up -d`, com projeto Compose isolado e porta alternativa. O serviço ficou healthy, com duas contas e 33 tarefas provisionadas automaticamente. Chamados e eventos começaram vazios nesse volume novo.

Antes da atualização local, foi criado um backup consistente pela API do SQLite, em arquivo privado dentro do volume. Após `docker compose up -d --build --wait`, a comparação confirmou os mesmos usuários, todos os campos anteriores dos três chamados, sessões, contadores e 33 identificadores/colunas do quadro. Chave de sessão e credenciais permaneceram idênticas. Os chamados anteriores receberam Média e não ganharam eventos inventados. A integridade SQLite e as chaves estrangeiras passaram na conferência.

O seed foi repetido duas vezes com resultado idêntico e sem duplicação. Depois, as 12 tarefas verificadas da Sprint 2 foram movidas para Concluído pelo fluxo autenticado do Kanban; as colunas das demais Sprints permaneceram iguais às do backup. O técnico conseguiu consultar os três chamados anteriores pela interface. A suíte final, com o catálogo concluído, passou novamente: 85 testes, sem warnings. Nenhum volume foi apagado.

Uma nova exportação consolidada iniciou (`helpdesk-sprint2-final-check`, porta 8084), seguida do fluxo completo de navegador e da recriação. As dez páginas/estados e a persistência passaram novamente. Na revisão de mensagens, um parâmetro de página não numérico ainda expunha a mensagem padrão em inglês; a rota passou a apresentar a orientação em português. O caso foi verificado no navegador nas quatro larguras e com axe, sem violações no escopo executado.

Após a padronização da mensagem, a suíte completa passou novamente com 85 testes, sem warnings.
