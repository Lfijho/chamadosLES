# Acompanhamento versionado

Este arquivo registra o trabalho verificado no código. O quadro da aplicação mantém o estado operacional no SQLite: alterações feitas nele não editam este documento. `docs/backlog.yml` é o catálogo inicial; sincronização insere tarefas ausentes e atualiza metadados, sem apagar tarefas ou sobrescrever a coluna persistida. Volumes anteriores podem manter colunas diferentes das descritas aqui, por decisão do usuário.

| Coluna | Tarefas | Evidência de aceite |
|---|---|---|
| Concluído | S1-01 — Autenticação | Login de ambos os perfis, limites por conta/IP, cookies, expiração e logout revogável: testes isolados e navegador |
| Concluído | S1-02 — Chamados | Validações, limites, CSRF, autor/status/UTC/protocolo, escape, PRG e propriedade: testes e navegador |
| Concluído | S1-03 — Interface | Fluxos, labels, foco, axe e viewports desktop/celular verificados no navegador |
| Concluído | S1-04 — Kanban | Perfil técnico, CSRF, coluna persistente e sincronização idempotente: testes e recriação |
| Concluído | S1-05 — Docker | Build, volume automático, migração, usuário sem root, HTTP healthy e persistência após recriação verificados |
| Em andamento | S1-06 — Testes e CI | 47 testes locais passaram na revalidação da entrega. CI remota permanece bloqueada por faturamento da conta, reconferido em 29/10/2026 |
| Concluído | S1-07 — Documentação | README, RF/RNF, regras, UC01–UC03, SCRUM individual, roteiro e limites revisados contra o código |
| Concluído | S1-08 — Diagramas | Quatro fontes PlantUML com SVG/PNG renderizados, inspecionados e referenciados |
| Backlog | S2-01 a S2-12 | Três resumos originais e nove tarefas detalhadas de consulta, atendimento e entrega; não implementados |
| Backlog | S3-01 a S3-13 | Três resumos originais e dez tarefas detalhadas de histórico, indicadores e entrega final; não implementados |
| A fazer | — | — |

S1-06 permanece em andamento exclusivamente pela verificação remota bloqueada; implementação da suíte e do workflow foi entregue. Não se declara CI remota aprovada. Evidências e limitações: [verificacoes.md](verificacoes.md). Não há reuniões ou datas de trabalho presumidas.


## Planejamento das Sprints 2 e 3

Esta atualização cadastra e documenta trabalho futuro; não implementa RF03–RF06. As 19 tarefas detalhadas novas começam em **Backlog**. Os seis IDs de resumo anteriores foram mantidos como agrupadores, sem recriar seus registros. Seus metadados agora indicam as tarefas detalhadas, e as prioridades dos entregáveis obrigatórios foram alinhadas para Alta. As oito tarefas da Sprint 1 mantêm metadados e colunas anteriores.

O catálogo [backlog.yml](backlog.yml) contém descrição e critérios completos de cada tarefa, além das metas e datas de entrega. Identificadores não são renumerados em sincronizações. Descrição e aceite são campos distintos no quadro; tarefas de catálogos antigos sem descrição continuam válidas. Registrar uma tarefa não comprova seu aceite.

### Sprint 2 — entrega em 12/11/2026

**Meta:** permitir consulta e gestão básica dos chamados.

| ID novo | Tarefa | Prioridade | Critério resumido |
|---|---|---|---|
| S2-04 | RF03 — Listar e visualizar | Alta | Listagem/detalhe com protocolo, título, categoria, status e abertura; solicitante vê somente os próprios; técnico vê todos; URL autorizada no servidor e estado vazio |
| S2-05 | RF03 — Filtrar chamados | Alta | Status e categoria combináveis e validados, visibilidade preservada, limpar filtros e aviso de nenhum resultado |
| S2-06 | RF04 — Definir prioridade | Alta | Baixa/Média/Alta somente pelo técnico; novos chamados recebem Média; requisições manipuladas do solicitante são bloqueadas |
| S2-07 | RF04 — Status e solução | Alta | Aberto → Em atendimento → Concluído terminal; técnico autorizado; solução não vazia e conclusão UTC persistidas; transições inválidas rejeitadas |
| S2-08 | Preparar eventos de status | Alta | Autor, data UTC e anterior/novo; evento e alteração na mesma transação; rollback conjunto; sem interface de histórico nesta Sprint |
| S2-09 | Testar consulta e atendimento | Alta | Isolamento, URL, filtros combinados, prioridade, transições, solução, eventos e tentativas não autorizadas cobertos por testes |
| S2-10 | Documentação e UML | Alta | Requisitos, casos de uso, especificações e sequências atualizados; classes e atividades do atendimento; PlantUML/SVG/PNG coerentes e inspecionados |
| S2-11 | Validar migrações e Compose | Alta | Dados da Sprint 1 preservados; saúde, persistência após recriação, responsividade e testes acumulados verificados |
| S2-12 | Preparar apresentação e revisão | Média | Roteiro dos dois perfis, revisão, retrospectiva e limitações reais, sem histórico de reuniões inventado |

Validação técnica e preparação da apresentação foram separadas para aplicar Alta ao entregável obrigatório e Média à preparação. S2-01 resume S2-04/S2-05; S2-02 resume S2-06 a S2-08; S2-03 resume S2-09 a S2-12.

### Sprint 3 — entrega em 03/12/2026

**Meta:** disponibilizar histórico, indicadores e entrega final.

| ID novo | Tarefa | Prioridade | Critério resumido |
|---|---|---|---|
| S3-04 | RF05 — Adicionar registros | Alta | Somente técnico inclui anotações não vazias; conteúdo, autor e UTC persistidos; sem edição/exclusão pela interface |
| S3-05 | RF05 — Consultar histórico | Alta | Anotações e status em ordem cronológica, com autor/data; técnico vê qualquer chamado e solicitante somente os próprios; não inventar eventos antigos |
| S3-06 | RF06 — Painel de indicadores | Alta | Contagens reais por status/prioridade exclusivas do técnico, incluindo zeros e atualização após alterações; sem métricas adicionais |
| S3-07 | Testar histórico e indicadores | Alta | Persistência, ordenação, autoria, isolamento, bloqueio de escrita do solicitante e contagens antes/depois |
| S3-08 | Segurança e regressão | Alta | Autenticação, autorização, CSRF, escape, validações, ausência de segredos e testes acumulados; fluxos completos dos dois perfis |
| S3-09 | Compose, backup e restauração | Alta | Clone limpo, migrações anteriores, seed idempotente, saúde e persistência; procedimento consistente de backup/restauração testado, sem cópia insegura do banco ativo |
| S3-10 | Documentação e diagramas finais | Alta | Requisitos, casos de uso/especificações, sequências, classes, atividades, README, execução, evidências e limites; fontes/SVG/PNG renderizados e conferidos |
| S3-11 | Preparar roteiro do vídeo | Média | Roteiro mostra dois perfis, RF01–RF06, permissões e Compose; não equivale a gravação/postagem |
| S3-12 | Gravar vídeo e entregar no LEX | Alta | Checklist/pacote conferidos, vídeo realmente gravado e postagem realmente realizada com evidência; documentação da intenção não conclui a tarefa |
| S3-13 | Encerrar acompanhamento | Média | Revisão e retrospectiva final reais; critérios conferidos; pendências mantidas visíveis; não concluir tarefas apenas por estarem documentadas |

S3-01 resume S3-04/S3-05; S3-02 resume S3-06; S3-03 resume S3-07 a S3-13. A preparação do roteiro foi separada da gravação e entrega obrigatórias para distinguir prioridades e evidências de conclusão.

## Sincronização e verificação desta atualização

O provisionamento existente continua inserindo somente IDs ausentes e atualizando metadados, sem apagar tarefas nem sobrescrever a coluna persistida. A nova migração `7b2f18c4a901` acrescenta apenas a descrição de tarefas, com valor vazio compatível com os registros anteriores; não modifica chamados ou implementa atendimento/histórico/indicadores.

Depois de obter esta branch, o comando abaixo reconstrói a imagem e aplica migração e sincronização automaticamente, conservando o volume existente:

```bash
docker compose up -d --build --wait
```

A sincronização pode ser repetida explicitamente sem duplicar registros:

```bash
docker compose exec app flask seed
docker compose exec app flask seed
```

Verificações executadas nesta alteração:

- Suíte completa: **47 testes passaram** em banco/estado temporários, incluindo os quatro testes novos de metadados do catálogo, duas importações com preservação, migração compatível e escape da descrição.
- No volume existente, foram aplicadas a migração aditiva e **duas importações explícitas** pelo CLI. Cada resultado foi comparado com uma referência obtida antes da migração: primeira importação com **+9 tarefas da Sprint 2 e +10 da Sprint 3**; segunda importação sem novos IDs e com resultado idêntico. Todas as novas colunas permaneceram em Backlog.
- Resultado do banco: **33 tarefas**, sendo 8 da Sprint 1, 12 da Sprint 2 e 13 da Sprint 3. Mantidos os 14 IDs anteriores e as respectivas colunas; nenhum registro removido. Os seis resumos originais continuam incluídos nesses totais.
- Comparação dos metadados anteriores da Sprint 1 e dos dados de usuários, chamados, sessões e limites de login não encontrou alterações. Chave e credenciais permaneceram idênticas. O banco de demonstração tinha dois usuários e nenhum chamado antes da atualização; o teste isolado também comprovou preservação de um chamado existente e de tarefas locais extras, com colunas diferentes do catálogo.
- `docker compose config --quiet`, build, migração, `flask db check` e recriação do serviço passaram, sem apagar volumes. O serviço ficou healthy; o provisionamento automático adicional na recriação também conservou o quadro.
- Kanban verificado no Chromium com 33 cartões e 19 novas descrições: axe sem violações nos escopos A/AA executados, foco de 3px visível e nenhuma rolagem horizontal em 320/390/768/1440px. Foram abertas e inspecionadas capturas dos cartões S2-07 e S3-12 em desktop/celular. CSS e sistema visual foram preservados.
- A revisão renderizada foi feita no navegador. Não houve certificação de acessibilidade ou teste em aparelho físico.

Os estados operacionais do banco podem mudar posteriormente por ação do técnico; o documento continua sendo um registro versionado, não uma cópia dinâmica do quadro.


## Documento acadêmico de entrega da Sprint 1

Foram preparados `docs/entrega-sprint-1.md`, `docs/entrega-sprint-1.docx` e `docs/entrega-sprint-1.pdf` a partir do mesmo conteúdo revisado. A exportação final tem 10 páginas A4, uma captura sintética e quatro desenhos UML incorporados. Fontes detalhadas anteriores foram preservadas; versões de leitura `entrega-*` e procedimento de geração foram versionados.

Requisitos, casos de uso, responsabilidades de Tech Lead e limites foram conferidos contra código, configurações, testes, backlog e Git. A redação não declara retrospectiva formal ou apresentação sem evidência. A inspeção de todas as páginas conferiu tabelas, imagens, legendas e numeração. A geração dos arquivos conclui esta atividade de documentação; S1-06 continua em andamento pela CI externa bloqueada, e as funcionalidades futuras permanecem no Backlog. Evidências atuais em [verificacoes.md](verificacoes.md), seção de revalidação para 29/10/2026.

## Versão objetiva do documento acadêmico

A entrega acadêmica foi reescrita com foco na apresentação do projeto, organização individual, requisitos, funcionalidades da Sprint 1 e três casos de uso. O documento reúne quatro diagramas UML simplificados, os dois comandos de inicialização e as próximas Sprints, em cinco páginas A4.

Markdown, DOCX e PDF foram regenerados do mesmo conteúdo final. A inspeção visual conferiu legibilidade, tabelas inteiras, paginação e ocupação das páginas. A fonte do corpo foi ampliada para 11 pontos e a das tabelas para 10,5 pontos. O gerador de documentos foi ajustado à estrutura de sete seções e quatro figuras.

Os relatórios técnicos e os diagramas detalhados anteriores foram preservados. O código da aplicação, as configurações de execução e os dados não foram alterados. Esta revisão substitui a versão acadêmica de dez páginas, sem modificar o andamento das tarefas de implementação.


## Organização dos arquivos versionados

Configurações locais de ferramentas foram retiradas do índice e excluídas de novas inclusões neste checkout. README, catálogo e registros técnicos mantêm as informações do produto, dos testes e das verificações realizadas. As capturas opcionais do navegador passam a usar `artifacts/browser/`, ignorado pelo Git. O documento acadêmico, a aplicação e os diagramas foram preservados.

Verificações deste bloco: 47 testes passaram em container com estado temporário; build e validação do Compose concluídos; sintaxe do script de navegador e diff conferidos. A inspeção dos arquivos rastreados incluiu textos, SVG, conteúdo XML do DOCX e texto extraído do PDF. Configurações locais e capturas permanecem ignoradas. Nenhum volume ou dado da aplicação foi alterado.
