# HelpDesk — roteiro dos slides (10 minutos)

Leandro Pinzon Filho · Laboratório de Engenharia de Software · Sprint 3

A duração de 10 minutos atende ao planejamento desta apresentação; não é um limite informado no trecho da atividade. A contextualização é breve, pois as Sprints 1 e 2 já foram apresentadas. O foco são RF05, RF06 e as atualizações da modelagem.

Abra [os slides](../apresentacao-helpdesk.html) no navegador. Use **F** para tela cheia, setas ou Espaço para avançar e **N** para consultar estas notas. As notas aparecem na mesma tela: mantenha-as fechadas durante o compartilhamento. Cada intervalo abaixo é um tempo sugerido; os slides não avançam automaticamente.

Prepare a aplicação antes, caso substitua as capturas por uma demonstração. Use somente dados de ensaio e nunca mostre a saída das credenciais na gravação.

## 00:00–00:20 · Slide 01 — HelpDesk

**Fala sugerida**

Este é o HelpDesk, meu projeto individual de Laboratório de Engenharia de Software. Vou contextualizar o sistema e apresentar as atualizações da Sprint 3: histórico, anotações e indicadores, junto com os diagramas correspondentes.

**Na tela:** Explique o slide; não leia os nomes de funções em voz alta.

## 00:20–01:00 · Slide 02 — Um lugar para acompanhar o suporte

**Fala sugerida**

O problema é a dispersão das solicitações de suporte. O HelpDesk reúne os pedidos e seu acompanhamento. O solicitante registra um problema e acompanha os próprios chamados. O técnico consulta todos e conduz o atendimento. Essa separação também vale para as informações do histórico: o solicitante não consegue consultar o chamado de outra pessoa.

**Na tela:** Explique o slide; não leia os nomes de funções em voz alta.

## 01:00–01:35 · Slide 03 — Três Sprints, uma evolução do produto

**Fala sugerida**

O trabalho foi dividido em três Sprints. As duas primeiras, já apresentadas, entregaram acesso, abertura, consulta e atendimento. A terceira acrescenta histórico e indicadores. Atuo como Tech Lead e desenvolvedor, acumulando as atividades do projeto. Usei práticas de Scrum adaptadas ao trabalho individual, com backlog, planejamento por Sprint, Kanban e revisão e retrospectiva técnicas.

**Na tela:** Explique o slide; não leia os nomes de funções em voz alta.

## 01:35–02:15 · Slide 04 — O que a Sprint 3 acrescentou

**Fala sugerida**

Os dois requisitos novos são RF05 e RF06. O histórico reúne as mudanças de status que a Sprint 2 já gravava e as novas anotações do técnico. O painel mostra totais por status e prioridade. Entre os requisitos não funcionais, destaco o acesso por perfil e propriedade, a ordenação estável dos registros e as contagens sem duplicação por eventos ou anotações.

**Na tela:** Explique o slide; não leia os nomes de funções em voz alta.

## 02:15–03:05 · Slide 05 — Novos casos de uso

**Fala sugerida**

Este recorte mostra os três casos de uso novos, dentro do limite HelpDesk. Os atores externos são solicitante e técnico. Ambos consultam histórico, mas o solicitante só acessa os próprios chamados. Apenas o técnico adiciona anotações e consulta indicadores. UC01 a UC07 permanecem no diagrama completo; UC05 foi atualizado para mostrar o histórico junto do detalhe. O Kanban não aparece porque acompanha o desenvolvimento, e não o atendimento.

**Na tela:** Aponte as associações dos atores. O botão abre o diagrama completo, se houver pergunta; não é necessário para cumprir o tempo.

## 03:05–03:45 · Slide 06 — Do uso às funções implementadas

**Fala sugerida**

As especificações ligam a ação do usuário às funções reais da aplicação. Para consultar o histórico, a página de detalhes chama get_history. Para registrar uma anotação, ticket_note coordena o envio e add_note inclui o registro. No painel, indicators chama get_indicators. Todos exigem autenticação e as permissões correspondentes. Os documentos contêm os fluxos e as tabelas completas por caso de uso.

**Na tela:** Explique o slide; não leia os nomes de funções em voz alta.

## 03:45–04:30 · Slide 07 — Atendimento registrado, sem perder o contexto

**Fala sugerida**

Estas são capturas do sistema com dados de ensaio. O histórico mostra, na mesma sequência, mudanças de status e anotações, identificando autor e data. O técnico escreve a observação no próprio detalhe. Texto vazio ou apenas espaços é rejeitado. A anotação é somente de inclusão e pode ser feita após a conclusão, sem reabrir ou alterar o atendimento. O solicitante vê o histórico do próprio chamado, mas não recebe esse formulário.

**Na tela:** Aponte os dois tipos de registro e o formulário. Se optar pela demonstração ao vivo, substitua este bloco pelo mesmo fluxo em um chamado de ensaio; não acrescente tempo.

## 04:30–05:15 · Slide 08 — Como o histórico é consultado

**Fala sugerida**

O usuário seleciona um chamado existente. A rota ticket_detail busca esse chamado respeitando o perfil. No ramo autorizado, ticket_detail_response pede o histórico a get_history. A consulta reúne StatusEvent e TicketNote com autor e data UTC. A interface mostra os registros ou um estado vazio. Chamado inexistente ou não visível segue o ramo de indisponibilidade. A sessão de persistência está identificada como infraestrutura.

**Na tela:** Explique o slide; não leia os nomes de funções em voz alta.

## 05:15–06:10 · Slide 09 — Como uma anotação é incluída

**Fala sugerida**

Nesta sequência, o técnico envia a anotação. A rota ticket_note busca o chamado antes de validar o formulário NoteForm. Se o formulário estiver inválido, orienta a correção e não inclui nada. No ramo válido mostrado aqui, add_note cria TicketNote com o autor autenticado, adiciona o registro e confirma a gravação. Depois, há redirecionamento ao histórico. Este recorte mostra o caminho sem falha de persistência; o documento consolidado detalha as exceções. Nenhum passo altera os dados de atendimento do chamado.

**Na tela:** Explique o slide; não leia os nomes de funções em voz alta.

## 06:10–06:45 · Slide 10 — Indicadores que refletem os chamados

**Fala sugerida**

Este é o painel do técnico. O exemplo contém um chamado concluído com prioridade Alta; as demais categorias aparecem com zero. Os dois agrupamentos contam o mesmo conjunto de chamados sob perspectivas diferentes, portanto não devemos somar uma tabela à outra. Os totais são recalculados ao acessar a página, e as anotações não aumentam a quantidade de chamados.

**Na tela:** Explique o slide; não leia os nomes de funções em voz alta.

## 06:45–07:15 · Slide 11 — Como os totais são calculados

**Fala sugerida**

A rota indicators solicita os dados a get_indicators. O perfil técnico é conferido e são feitas duas consultas agregadas: uma por status e outra por prioridade. Elas contam diretamente os chamados, sem juntar os registros do histórico. As opções ausentes recebem zero. Por isso, vários eventos e anotações do mesmo chamado não duplicam o total.

**Na tela:** Explique o slide; não leia os nomes de funções em voz alta.

## 07:15–08:05 · Slide 12 — O modelo agora inclui as anotações

**Fala sugerida**

O modelo mantém User, Ticket e StatusEvent e acrescenta TicketNote. Cada chamado pertence a um solicitante. Cada anotação pertence a um chamado e a um autor, enquanto cada evento identifica o técnico que mudou o status. Um chamado pode ter nenhum ou vários eventos e anotações. O desenho mostra atributos e operações reais selecionados. A barra em protocol indica uma propriedade derivada. As operações de coordenação do histórico são funções de módulo, e não métodos inventados nessas classes.

**Na tela:** Explique o slide; não leia os nomes de funções em voz alta.

## 08:05–08:35 · Slide 13 — Consultar conforme o perfil

**Fala sugerida**

O diagrama de atividades separa as responsabilidades de solicitante, HelpDesk e técnico. O perfil define quais chamados podem ser selecionados. O sistema consulta os registros reais do chamado autorizado e apresenta o histórico. Para o solicitante, a consulta termina aqui. O conector A leva ao trecho opcional de anotações do técnico.

**Na tela:** Explique o slide; não leia os nomes de funções em voz alta.

## 08:35–09:15 · Slide 14 — Anotar é uma ação opcional

**Fala sugerida**

Na continuação, o técnico decide se quer adicionar uma anotação. Se não quiser, encerra essa interação. Se quiser, escreve e envia. O sistema valida o texto; quando há erro, orienta a correção. O retorno à decisão também permite cancelar. Com texto válido, inclui o registro e mostra o histórico atualizado. Esse fluxo não exige anotar para concluir um chamado e não reabre chamados concluídos.

**Na tela:** Explique o slide; não leia os nomes de funções em voz alta.

## 09:15–09:50 · Slide 15 — Como acessar a entrega

**Fala sugerida**

A aplicação mantém a stack do projeto: Flask, páginas HTML e CSS e SQLite. O Docker Compose permite iniciar o sistema, e o segundo comando consulta as credenciais locais de demonstração. O acesso é em localhost, porta 8080. Para apresentar, deixo a aplicação e as sessões prontas antes de começar. O foco da entrega está nas novas funções e em sua relação com a modelagem; não é necessário aguardar a construção da imagem durante a fala.

**Na tela:** Não execute demo-credentials na tela compartilhada. Se a imagem já existir e o código tiver mudado, prepare antes com docker compose up -d --build.

## 09:50–10:00 · Slide 16 — Do pedido ao registro do atendimento

**Fala sugerida**

A Sprint 3 acrescenta o registro do atendimento, o histórico por chamado e os indicadores do técnico. Obrigado.

**Na tela:** Explique o slide; não leia os nomes de funções em voz alta.
