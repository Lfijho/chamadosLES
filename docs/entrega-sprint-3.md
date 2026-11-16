# HelpDesk: entrega final da Sprint 3

Disciplina: Laboratório de Engenharia de Software\
Projeto: HelpDesk | Sistema de Controle de Chamados de TI\
Integrante: Leandro Pinzon Filho | Desenvolvimento individual\
Papel: Tech Lead e desenvolvedor responsável | Entrega final: 03/12/2026\
Repositório: <https://github.com/Lfijho/chamadosLES>

## 1. Objetivo e organização

O HelpDesk centraliza solicitações de suporte de TI que, quando dispersas, dificultam o registro dos problemas e o acompanhamento do atendimento. O solicitante registra e consulta os próprios chamados. O técnico consulta as solicitações e conduz o atendimento até a conclusão.

Leandro Pinzon Filho desenvolve o projeto individualmente, como Tech Lead e responsável por requisitos, planejamento, implementação, testes, documentação e apresentação. O trabalho adota práticas de Scrum adaptadas ao desenvolvimento individual: backlog, planejamento em três Sprints, acompanhamento pelo Kanban e revisão e retrospectiva técnicas. O quadro usa as colunas Backlog, A fazer, Em andamento e Concluído e acompanha o desenvolvimento, separado do atendimento dos chamados.

A Sprint 1 entregou acesso e abertura de chamados. A Sprint 2 acrescentou consulta e atendimento. A Sprint 3 reúne histórico e indicadores à aplicação. As entregas anteriores permanecem como registro histórico.

## 2. Escopo e requisitos

| Código | Funcionalidade | Sprint | Situação nesta entrega |
|---|---|---|---|
| RF01 | Autenticar usuários | 1 | Disponível |
| RF02 | Abrir chamado | 1 | Disponível |
| RF03 | Consultar chamados | 2 | Disponível |
| RF04 | Atualizar atendimento | 2 | Disponível |
| RF05 | Registrar e consultar histórico | 3 | Disponível |
| RF06 | Consultar painel de indicadores | 3 | Disponível |

| Código | Requisito não funcional |
|---|---|
| RNF13 | Restringir consultas e alterações conforme o perfil e a propriedade do chamado |
| RNF03 | Proteger as senhas e exigir autenticação para acessar as páginas restritas |
| RNF07 | Preservar dados entre reinicializações e nas atualizações das Sprints |
| RNF09 | Oferecer telas em português, labels, foco de teclado e adaptação a diferentes telas |
| RNF04 | Validar formulários no servidor e proteger as operações que alteram dados |
| RNF01 | Permitir inicialização pelo Docker Compose com a configuração do projeto |
| RNF14 | Ordenar o histórico por data UTC, com desempate estável e identificação do autor |
| RNF15 | Calcular contagens dos chamados no banco, sem duplicação pelos registros do histórico |

<!-- pagebreak -->

## 3. Funcionalidades e regras de atendimento

A aplicação utiliza Python com Flask, páginas HTML/CSS e SQLite, com execução por Docker Compose. A Sprint 1 oferece login por e-mail e senha, logout e abertura de chamado. Título tem de 5 a 120 caracteres; descrição, de 10 a 5.000. As categorias são Hardware, Software, Rede, Acessos e Outros. A abertura gera protocolo e confirmação em nome do solicitante autenticado.

A Sprint 2 permite consultar chamados, combinar filtros de status e categoria e navegar por páginas de dez registros, dos mais recentes para os mais antigos. O solicitante vê somente os próprios chamados; o técnico vê todos. O detalhe apresenta protocolo, título, descrição, categoria, solicitante, abertura, status, prioridade e solução quando existente.

As regras de atendimento são:

- Somente o técnico pode alterar prioridade, status ou solução.
- A prioridade é Baixa, Média ou Alta. Chamados novos e os preservados da Sprint 1 recebem Média inicialmente.
- O fluxo é Aberto → Em atendimento → Concluído. Concluído é terminal e fica disponível para consulta.
- A conclusão exige solução com 1 a 5.000 caracteres após remover espaços externos, além da data de conclusão em UTC.
- Alterações inválidas preservam os dados anteriores. Se o chamado mudou desde a abertura da página, o técnico precisa revisar os dados atualizados.
- Cada mudança de status grava autor, data UTC e valores anterior e novo junto com a alteração do chamado. O detalhe exibe esses eventos junto com as anotações de atendimento.

A Sprint 3 permite ao técnico incluir anotações de 1 a 5.000 caracteres após remover espaços externos. O conteúdo é exibido como texto, com autor autenticado e data UTC. As anotações são somente de inclusão: não há edição ou exclusão. É possível acrescentar uma observação depois da conclusão, sem mudar status, prioridade ou solução.

O histórico é cronológico. Quando datas coincidem, eventos de status aparecem antes das anotações; dentro do mesmo tipo, o identificador define a ordem. Chamados antigos mostram apenas os registros existentes. O solicitante consulta o próprio histórico e o técnico consulta qualquer chamado.

O painel exclusivo do técnico apresenta contagens por status e prioridade, incluindo valores zero. As consultas contam chamados, independentemente da quantidade de registros de atendimento. Ao abrir novamente a página, as contagens são recalculadas.

<!-- pagebreak -->

## 4. Casos de uso e funções envolvidas

UC01, UC02 e UC03 pertencem à Sprint 1. UC04 a UC07 foram acrescentados na Sprint 2. UC08 a UC10 pertencem à Sprint 3; UC05 passa a incluir o histórico no detalhe. As tabelas identificam funções implementadas no projeto. Funções de módulo estão indicadas pelo nome do módulo, sem atribuição a uma classe de controller. Nas sequências, validate() e validate_on_submit() são operações herdadas de FlaskForm.

### UC01: realizar login

Ator: solicitante ou técnico. Objetivo: acessar as funções do perfil. Precondição: possuir uma conta.

1. O usuário informa e-mail e senha.
2. O sistema verifica os dados.
3. O sistema permite o acesso e apresenta a página inicial do perfil.

Alternativas: dados inválidos mantêm o formulário para uma nova tentativa. Campos incompletos recebem orientação. Após tentativas repetidas, o sistema solicita que o usuário aguarde.

Pós-condição: o usuário acessa as funções do próprio perfil quando a autenticação é aceita.

| Método/função real | Classe ou módulo | Responsabilidade |
|---|---|---|
| `login` | `helpdesk.routes` | Coordenar o acesso |
| `authenticate` | `helpdesk.security` | Verificar as credenciais |
| `check_password` | `User`, em `helpdesk.models` | Conferir a senha da conta |
| `start_session` | `helpdesk.security` | Iniciar o acesso autenticado |

<!-- pagebreak -->

### UC02: realizar logout

Ator: solicitante ou técnico. Objetivo: sair da conta. Precondição: estar autenticado.

1. O usuário seleciona Sair.
2. O sistema encerra o acesso atual.
3. A página de login apresenta a confirmação da saída.

Alternativa: se o acesso já expirou, o sistema solicita novo login para acessar as páginas restritas.

Pós-condição: o usuário precisa se autenticar novamente para voltar às funções restritas.

| Método/função real | Classe ou módulo | Responsabilidade |
|---|---|---|
| `logout` | `helpdesk.routes` | Encerrar o acesso e retornar ao login |
| `login` | `helpdesk.routes` | Apresentar o formulário após a saída |

### UC03: abrir chamado

Ator: solicitante. Objetivo: registrar um problema de TI. Precondição: estar autenticado como solicitante.

1. O solicitante seleciona Abrir chamado.
2. O solicitante informa título, descrição e categoria e envia o formulário.
3. O sistema valida os dados e registra o chamado em nome do solicitante.
4. O sistema apresenta a confirmação, o protocolo e o status Aberto. O chamado recebe prioridade Média.

Alternativas: campos inválidos recebem orientação antes de salvar. O técnico não pode abrir chamados. A confirmação anterior continua acessível ao autor.

Pós-condição: o chamado fica registrado e disponível na consulta do solicitante e do técnico.

| Método/função real | Classe ou módulo | Responsabilidade |
|---|---|---|
| `new_ticket` | `helpdesk.routes` | Receber e validar o formulário |
| `create_ticket` | `helpdesk.tickets` | Registrar o chamado do solicitante |
| `ticket_confirmation` | `helpdesk.routes` | Apresentar a confirmação privada |
| `get_ticket` | `helpdesk.tickets` | Buscar o chamado com permissão de consulta |
| `visible_tickets` | `helpdesk.tickets` | Restringir a confirmação ao solicitante |

<!-- pagebreak -->

### UC04: consultar chamados e filtrar

Ator: solicitante ou técnico. Objetivo: localizar solicitações. Precondição: estar autenticado.

1. O usuário acessa Meus chamados ou Chamados, conforme o perfil.
2. O sistema lista os registros que o usuário pode consultar.
3. O usuário combina status e categoria, aplica ou limpa os filtros.
4. O usuário navega entre as páginas, mantendo os filtros escolhidos.

Alternativas: lista vazia orienta o próximo passo; busca sem resultados permite alterar ou limpar os filtros. Parâmetros inválidos recebem orientação. Página inexistente informa que o recurso não foi encontrado.

Pós-condição: a consulta mantém a visibilidade do perfil, inclusive ao alterar parâmetros.

| Método/função real | Classe ou módulo | Responsabilidade |
|---|---|---|
| `ticket_list` | `helpdesk.routes` | Validar os parâmetros e apresentar a consulta |
| `visible_tickets` | `helpdesk.tickets` | Restringir registros conforme o perfil |
| `list_tickets` | `helpdesk.tickets` | Aplicar filtros, ordenação e paginação |

### UC05: consultar detalhes

Ator: solicitante ou técnico. Objetivo: consultar os dados de um chamado. Precondição: estar autenticado e ter permissão sobre o registro.

1. O usuário seleciona um chamado na lista.
2. O sistema verifica a permissão e busca os dados.
3. O sistema apresenta o detalhe, o histórico e as ações permitidas ao perfil.

Alternativas: chamado inexistente ou não visível ao usuário atual não é exibido, inclusive por acesso direto ao endereço. O técnico pode consultar chamados de qualquer solicitante. Chamados concluídos apresentam a solução, sem edição de status, prioridade ou solução.

Pós-condição: o usuário consulta o chamado sem modificar seus dados.

| Método/função real | Classe ou módulo | Responsabilidade |
|---|---|---|
| `ticket_detail` | `helpdesk.routes` | Coordenar a abertura do detalhe |
| `get_ticket` | `helpdesk.tickets` | Buscar somente um registro autorizado |
| `visible_tickets` | `helpdesk.tickets` | Aplicar a visibilidade do perfil |
| `ticket_detail_response` | `helpdesk.routes` | Apresentar os dados e as ações disponíveis |
| `get_history` | `helpdesk.tickets` | Reunir os registros autorizados do chamado |

<!-- pagebreak -->

### UC06: definir prioridade

Ator: técnico. Objetivo: organizar a prioridade do atendimento. Precondições: estar autenticado como técnico e consultar um chamado não concluído.

1. O técnico seleciona Baixa, Média ou Alta no detalhe.
2. O técnico seleciona Salvar prioridade.
3. O sistema valida a alteração e apresenta a confirmação.

Alternativas: prioridade inválida é rejeitada. Solicitante não pode realizar a alteração. Chamado concluído permanece sem edição. Se os dados mudaram, o sistema solicita revisão da página atualizada.

Pós-condição: a prioridade válida fica persistida; uma rejeição mantém os dados anteriores.

| Método/função real | Classe ou módulo | Responsabilidade |
|---|---|---|
| `ticket_priority` | `helpdesk.routes` | Coordenar a alteração da prioridade |
| `get_ticket` | `helpdesk.tickets` | Buscar o chamado autorizado |
| `ticket_detail_response` | `helpdesk.routes` | Apresentar o detalhe em caso de rejeição |
| `update_priority` | `helpdesk.tickets` | Coordenar a gravação autorizada |
| `check_edit` | `helpdesk.tickets` | Verificar perfil, versão e estado do chamado |
| `set_priority` | `Ticket`, em `helpdesk.models` | Validar e atribuir a prioridade |

<!-- pagebreak -->

### UC07: atualizar status e registrar solução

Ator: técnico. Objetivo: conduzir e concluir o atendimento. Precondições: estar autenticado como técnico e consultar um chamado não concluído.

1. O técnico seleciona Iniciar atendimento para um chamado Aberto e envia essa ação.
2. O sistema registra Em atendimento e confirma a alteração.
3. Mais tarde, o técnico informa a solução e envia uma nova ação: Concluir chamado.
4. O sistema valida a solução, registra Concluído e a data de conclusão e apresenta a confirmação.

Iniciar e concluir são ações separadas. Cada envio solicita somente a próxima transição permitida.

Alternativas: solução vazia, composta apenas por espaços ou acima do limite exige correção. Saltos, retrocessos, alterações em chamados concluídos e operações do solicitante são rejeitados. Em conflito ou falha de gravação, a operação não confirma alterações parciais.

Pós-condição: a mudança de status e seu evento com autoria e data UTC ficam persistidos juntos. Após a conclusão, o chamado permanece disponível para consulta.

| Método/função real | Classe ou módulo | Responsabilidade |
|---|---|---|
| `ticket_status` | `helpdesk.routes` | Coordenar uma transição por requisição |
| `get_ticket` | `helpdesk.tickets` | Buscar o chamado autorizado |
| `validate_solution` | `StatusForm`, em `helpdesk.forms` | Exigir conteúdo na solução ao concluir |
| `ticket_detail_response` | `helpdesk.routes` | Apresentar o detalhe em caso de rejeição |
| `check_edit` | `helpdesk.tickets` | Verificar perfil, versão e estado do chamado |
| `update_status` | `helpdesk.tickets` | Gravar a mudança e o evento juntos |
| `change_status` | `Ticket`, em `helpdesk.models` | Validar a transição e atribuir solução e conclusão |

<!-- pagebreak -->

### UC08: consultar histórico

Ator: solicitante ou técnico. Objetivo: acompanhar as ações registradas. Precondições: estar autenticado e poder consultar o chamado.

1. O usuário abre os detalhes de um chamado e consulta Histórico do chamado.
2. O sistema verifica a permissão e reúne as mudanças de status e anotações existentes.
3. O sistema apresenta os registros em ordem cronológica, com autor e data UTC.

Alternativas: chamado inexistente ou não visível não é exibido. Sem registros, o sistema apresenta o histórico vazio. O técnico pode consultar qualquer chamado; o solicitante, somente os próprios.

Pós-condição: o usuário consulta os registros existentes, sem alterar o chamado ou criar eventos antigos.

| Método/função real | Classe ou módulo | Responsabilidade |
|---|---|---|
| `ticket_detail` | `helpdesk.routes` | Coordenar a consulta do detalhe |
| `get_ticket` | `helpdesk.tickets` | Buscar um chamado autorizado |
| `visible_tickets` | `helpdesk.tickets` | Restringir a busca pelo perfil |
| `ticket_detail_response` | `helpdesk.routes` | Apresentar detalhe e histórico |
| `get_history` | `helpdesk.tickets` | Conferir acesso, reunir e ordenar registros |

<!-- pagebreak -->

### UC09: adicionar anotação

Ator: técnico. Objetivo: registrar uma ação ou observação. Precondições: estar autenticado como técnico e consultar um chamado existente.

1. O técnico escreve a anotação no detalhe e seleciona Registrar anotação.
2. O sistema valida o conteúdo e associa o registro ao chamado e ao técnico autenticado.
3. O sistema grava a data UTC e apresenta a confirmação no histórico.

Alternativas: texto vazio, composto só por espaços ou acima de 5.000 caracteres exige correção. Chamado inexistente não recebe registro. Solicitantes não podem incluir anotações. Uma falha de gravação não confirma a inclusão.

Pós-condição: a anotação fica disponível no histórico, sem edição ou exclusão. Mesmo após a conclusão, a inclusão mantém status, prioridade e solução.

| Método/função real | Classe ou módulo | Responsabilidade |
|---|---|---|
| `ticket_note` | `helpdesk.routes` | Receber o formulário e apresentar o resultado |
| `get_ticket` | `helpdesk.tickets` | Buscar o chamado autorizado |
| `add_note` | `helpdesk.tickets` | Validar e incluir a anotação do técnico |
| `ticket_detail_response` | `helpdesk.routes` | Apresentar o detalhe em caso de rejeição |

### UC10: consultar indicadores

Ator: técnico. Objetivo: consultar a distribuição dos chamados. Precondição: estar autenticado como técnico.

1. O técnico seleciona Indicadores.
2. O sistema conta os chamados por status e por prioridade.
3. O sistema apresenta os dois agrupamentos, com zero nas opções sem registros.

Alternativas: solicitantes não acessam o painel. Sem chamados, todas as contagens são zero.

Pós-condição: o técnico consulta os valores atuais; anotações e eventos não multiplicam as contagens.

| Método/função real | Classe ou módulo | Responsabilidade |
|---|---|---|
| `indicators` | `helpdesk.routes` | Apresentar o painel exclusivo do técnico |
| `get_indicators` | `helpdesk.tickets` | Agregar chamados por status e prioridade |

## 5. Execução

Na pasta do projeto, execute:

```bash
docker compose up -d
docker compose exec app flask demo-credentials
```

Acesso: `http://localhost:8080`. O segundo comando permite consultar localmente as credenciais de demonstração. Após atualizar uma imagem já construída, execute `docker compose up -d --build`.

<!-- pagebreak -->

## 6. Modelagem UML

### 6.1. Casos de uso

![Figura 1. Casos de uso das três Sprints.](diagrams/sprint-3-use-cases.png){width=16.5cm height=21cm}

UC01 a UC07 mantêm as ações das entregas anteriores. UC08, UC09 e UC10 acrescentam histórico, anotações e indicadores, com os atores associados às funções de seus perfis; o Kanban permanece separado.

<!-- landscape -->

### 6.2. Sequência do login

![Figura 2. Realizar login.](diagrams/sprint-2-login.png){width=26cm height=15cm}

O módulo de rotas coordena a autenticação com o módulo de acesso e o objeto User.

<!-- pagebreak -->

### 6.3. Sequência do logout

![Figura 3. Realizar logout.](diagrams/sprint-2-logout.png){width=24cm height=15cm}

A saída encerra o acesso atual e retorna à página de login.

<!-- pagebreak -->

### 6.4. Sequência da abertura

![Figura 4. Abrir chamado.](diagrams/sprint-2-open-ticket.png){width=26cm height=15cm}

O formulário valida os dados e a abertura associa o chamado ao solicitante autenticado.

<!-- pagebreak -->

### 6.5. Sequência da consulta e dos filtros

![Figura 5. Consultar chamados e filtrar.](diagrams/sprint-2-list-tickets.png){width=26cm height=15cm}

Filtros inválidos impedem a consulta; a primeira página aceita resultado vazio, e uma página além dos resultados é tratada como inexistente.

<!-- pagebreak -->

### 6.6. Sequência da consulta de detalhes

![Figura 6. Consultar detalhes com histórico.](diagrams/sprint-3-ticket-detail.png){width=26cm height=15cm}

A busca autorizada antecede a apresentação dos dados e do histórico. O técnico pode consultar chamados de qualquer solicitante.

<!-- pagebreak -->

### 6.7. Sequência da prioridade

![Figura 7. Definir prioridade: busca e formulário.](diagrams/sprint-2-priority.png){width=26cm height=15cm}

A busca autorizada antecede a validação do formulário e a atualização.

<!-- pagebreak -->

### 6.7. Sequência da prioridade (continuação)

![Figura 7 (continuação). Atualização e tratamento do resultado.](diagrams/sprint-2-priority_001.png){width=26cm height=15cm}

Regra violada, conflito e falha de persistência recebem tratamentos distintos.

<!-- pagebreak -->

### 6.8. Sequência do status e da solução

![Figura 8. Atualizar status: busca e formulário.](diagrams/sprint-2-status.png){width=26cm height=15cm}

Iniciar e concluir são ações separadas. Cada requisição solicita apenas uma transição.

<!-- pagebreak -->

### 6.8. Sequência do status e da solução (continuação)

![Figura 8 (continuação). Transição e persistência do evento.](diagrams/sprint-2-status_001.png){width=26cm height=15cm}

A alteração do Ticket e o StatusEvent são gravados na mesma transação.

<!-- pagebreak -->

### 6.9. Sequência da consulta do histórico

![Figura 9. Consultar histórico.](diagrams/sprint-3-history.png){width=26cm height=15cm}

A consulta reúne somente registros existentes e respeita a permissão sobre o chamado.

<!-- pagebreak -->

### 6.10. Sequência da inclusão de anotação

![Figura 10. Adicionar anotação: busca e formulário.](diagrams/sprint-3-note.png){width=26cm height=15cm}

Somente o técnico envia uma anotação. A inclusão depende da validação do formulário.

<!-- pagebreak -->

### 6.10. Sequência da inclusão de anotação (continuação)

![Figura 10 (continuação). Inclusão e tratamento do resultado.](diagrams/sprint-3-note_001.png){width=26cm height=15cm}

A operação grava autor e data UTC sem modificar os dados do chamado, inclusive após a conclusão.

<!-- pagebreak -->

### 6.11. Sequência dos indicadores

![Figura 11. Consultar indicadores.](diagrams/sprint-3-indicators.png){width=26cm height=15cm}

As consultas agregam chamados por status e prioridade, sem juntar os registros do histórico.

<!-- pagebreak -->

### 6.12. Classes e operações

![Figura 12. Classes principais da aplicação.](diagrams/sprint-3-classes.png){width=26cm height=15cm}

TicketNote relaciona cada anotação a um chamado e a um autor. O sinal + indica membros públicos, e /protocol representa uma propriedade derivada.

<!-- pagebreak -->

### 6.13. Atividades do atendimento

![Figura 13. Abertura e início do atendimento.](diagrams/sprint-3-activities.png){width=26cm height=15cm}

A alteração da prioridade é opcional. O conector A continua o fluxo na página seguinte.

<!-- portrait -->

### 6.13. Atividades do atendimento (continuação)

![Figura 13 (continuação). Anotação opcional, conclusão e consulta do histórico.](diagrams/sprint-3-activities_001.png){width=17cm height=20cm}

## 7. Entrega final

RF01 a RF06 estão disponíveis nesta versão. A gravação do vídeo, a apresentação e a postagem no LEX permanecem pendentes. O Kanban registra as tarefas do desenvolvimento; ele não substitui o atendimento dos chamados.
