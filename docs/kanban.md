# Acompanhamento versionado

Este arquivo registra o trabalho verificado no código. O quadro da aplicação mantém o estado operacional no SQLite: alterações feitas nele não editam este documento. `docs/backlog.yml` é o catálogo inicial; sincronização insere tarefas ausentes e atualiza metadados, sem apagar tarefas ou sobrescrever a coluna persistida. Volumes anteriores podem manter colunas diferentes das descritas aqui, por decisão do usuário.

| Coluna | Tarefas | Evidência de aceite |
|---|---|---|
| Concluído | S1-01 — Autenticação | Login de ambos os perfis, limites por conta/IP, cookies, expiração e logout revogável: testes isolados e navegador |
| Concluído | S1-02 — Chamados | Validações, limites, CSRF, autor/status/UTC/protocolo, escape, PRG e propriedade: testes e navegador |
| Concluído | S1-03 — Interface | Fluxos, labels, foco, axe e viewports desktop/celular verificados no navegador |
| Concluído | S1-04 — Kanban | Perfil técnico, CSRF, coluna persistente e sincronização idempotente: testes e recriação |
| Concluído | S1-05 — Docker | Build, volume automático, migração, usuário sem root, HTTP healthy e persistência após recriação verificados |
| Em andamento | S1-06 — Testes e CI | 43 testes passaram e workflow foi entregue. Confirmação de execução no GitHub bloqueada por faturamento da conta |
| Concluído | S1-07 — Documentação | README, RF/RNF, regras, UC01–UC03, SCRUM individual, roteiro e limites revisados contra o código |
| Concluído | S1-08 — Diagramas | Quatro fontes PlantUML com SVG/PNG renderizados, inspecionados e referenciados |
| Backlog | S2-01, S2-02, S2-03 | RF03/RF04 e testes/documentação futuros; não implementados |
| Backlog | S3-01, S3-02, S3-03 | RF05/RF06 e revisão futura; não implementados |
| A fazer | — | — |

S1-06 permanece em andamento exclusivamente pela verificação remota bloqueada; implementação da suíte e do workflow foi entregue. Não se declara CI remota aprovada. Evidências e limitações: [verificacoes.md](verificacoes.md). Não há reuniões ou datas de trabalho presumidas.
