# Roteiro do vídeo da Sprint 3

Projeto: HelpDesk — Sistema de Controle de Chamados de TI. Disciplina: Laboratório de Engenharia de Software. Responsável: Leandro Pinzon Filho. Entrega do vídeo e postagem no LEX: 03/12/2026.

As Sprints 1 e 2 já foram apresentadas, conforme informado pelo responsável. Este vídeo apresenta as atualizações da Sprint 3: RF05, RF06, requisitos atualizados, casos de uso e especificações, sequências, classes, atividades e implementação. O documento consolidado continua reunindo as três Sprints; durante a apresentação, destaque os trechos alterados.

**Duração sugerida: 6 minutos e 30 segundos.** O trecho da atividade fornecido não informa duração mínima ou máxima. Os tempos abaixo organizam a gravação; não são uma regra da disciplina.

Situação: roteiro preparado. Gravação, apresentação e postagem referentes à Sprint 3 permanecem pendentes.

## Preparação fora da gravação

- Deixe a aplicação funcionando em `http://localhost:8080` e o PDF `docs/entrega-sprint-3.pdf` aberto.
- Prepare um chamado de exemplo com registros de status. Se precisar abrir um chamado ou avançar seu atendimento para preparar os dados, faça isso antes da gravação, pelos fluxos normais da aplicação.
- Deixe o perfil técnico aberto em uma janela e o solicitante do chamado em outra sessão, por exemplo em uma janela anônima. A troca de perfil serve para demonstrar as novas permissões.
- Separe as páginas do PDF: requisitos na página 1; UC05 na 5; UC08 na 8; UC09 e UC10 na 9; casos de uso na 10; detalhe atualizado na 15; novas sequências nas 20–23; classes na 24; atividades nas 25–26. A numeração corresponde à versão atual de 26 páginas.
- Recupere as credenciais antes de gravar, em terminal privado. Não mostre senhas, cookies, chaves ou arquivos de estado. Use dados de exemplo.

## Gravação por tempo

| Tempo | O que mostrar ou fazer | Fala sugerida |
|---|---|---|
| **00:00–00:20** | Mostrar a identificação da entrega no PDF. | “Sou Leandro Pinzon Filho. Nesta apresentação vou mostrar as atualizações da Sprint 3 do HelpDesk: histórico de atendimento, indicadores e a documentação correspondente.” |
| **00:20–00:55** | Mostrar RF05 e RF06 na tabela de requisitos, além das regras de acesso e dos requisitos de ordenação e contagens. | “O RF05 acrescenta anotações e consulta do histórico. O RF06 acrescenta indicadores por status e prioridade. As atualizações incluem permissões, autoria, datas em UTC, ordenação estável e contagens sem duplicação.” |
| **00:55–01:40** | No diagrama de casos de uso, apontar UC08, UC09 e UC10. Mostrar suas especificações e tabelas de funções; mencionar a atualização do detalhe em UC05. | “Foram acrescentados consultar histórico, adicionar anotação e consultar indicadores. Os dois perfis consultam o histórico conforme a permissão; somente o técnico escreve anotações e acessa indicadores. As especificações identificam as funções reais utilizadas.” |
| **01:40–02:25** | Mostrar as novas sequências: histórico, inclusão de anotação e indicadores. Apontar `get_history()`, `add_note()` e `get_indicators()`. | “As sequências mostram a consulta autorizada, a validação antes de incluir uma anotação e as consultas agregadas do painel. A sessão de persistência aparece como infraestrutura, separada das responsabilidades da aplicação.” |
| **02:25–03:00** | Mostrar o diagrama de classes, destacando `TicketNote`, seus dados e as relações com `Ticket` e `User`. | “TicketNote foi acrescentada para armazenar conteúdo, autor e data da anotação. Cada anotação pertence a um chamado e a um autor. StatusEvent foi reaproveitada para preservar as mudanças de status já registradas.” |
| **03:00–03:35** | Mostrar a atualização do diagrama de atividades: decisão de anotar, correção de conteúdo e consulta do histórico pelos perfis. | “O fluxo passou a mostrar a anotação como uma ação opcional e a consulta do histórico. Registrar uma anotação não é uma condição obrigatória para concluir o atendimento.” |
| **03:35–04:40** | Como técnico, abrir o detalhe do chamado preparado. Mostrar o histórico, tentar enviar uma anotação só com espaços, corrigir e registrar uma anotação válida. | “No detalhe, o histórico reúne os eventos de status existentes e as anotações. O sistema rejeita texto vazio. A anotação válida recebe o autor autenticado e a data UTC e aparece na ordem cronológica, sem controles de edição ou exclusão.” |
| **04:40–05:20** | Abrir Indicadores. Mostrar os agrupamentos por status e prioridade e explicar os valores zero. Se usar duas abas, comparar as contagens antes e depois da anotação. | “O painel conta os chamados armazenados, por status e prioridade, e mostra zero quando não há registros naquela opção. Uma nova anotação não aumenta essas contagens, pois elas representam chamados.” |
| **05:20–06:00** | Na sessão do solicitante, abrir o mesmo chamado. Mostrar o histórico sem formulário de inclusão e tentar acessar `/indicadores`. | “O solicitante acompanha o histórico dos próprios chamados, mas não pode adicionar anotações. O painel também é restrito ao técnico, inclusive quando o solicitante tenta acessar seu endereço diretamente.” |
| **06:00–06:30** | Voltar à identificação do documento ou aos novos casos de uso e encerrar. | “Essas são as atualizações da Sprint 3: histórico, anotações e indicadores, acompanhados dos requisitos, especificações e diagramas atualizados. A entrega reúne essa documentação, a implementação e o vídeo.” |

Texto de exemplo para a anotação: “Realizada análise complementar da configuração de rede.”

## Limites do roteiro

Login, abertura, filtros, prioridade e mudança de status pertencem às Sprints já apresentadas. Neste vídeo, use essas funções somente para chegar às telas e preparar o exemplo. Não reserve blocos para reapresentá-las, para explicar novamente a stack ou para demonstrar o Docker.

O Kanban continua como ferramenta auxiliar; não é um artefato solicitado no trecho da atividade para este vídeo. A gravação concentra-se nas atualizações documentais e na implementação de RF05 e RF06.
