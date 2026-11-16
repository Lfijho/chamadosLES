# Roteiro do vídeo final

Projeto: HelpDesk — Sistema de Controle de Chamados de TI. Disciplina: Laboratório de Engenharia de Software. Responsável: Leandro Pinzon Filho, Tech Lead e desenvolvedor. Entrega prevista: 03/12/2026.

Situação: roteiro preparado. Vídeo não gravado; apresentação e postagem no LEX pendentes.

## Preparação

Use dados sintéticos. Recupere as credenciais com `docker compose exec app flask demo-credentials` antes da gravação, em um terminal privado. Não inclua senhas, cookies, chaves ou arquivos de estado no vídeo. Mantenha a aplicação em `http://localhost:8080` e o PDF final disponível.

## Sequência sugerida

1. **Execução:** mostre `docker compose up -d` e a aplicação no navegador. Se a imagem foi construída antes de atualizar o código, use `docker compose up -d --build`. Identifique o projeto e o desenvolvimento individual.
2. **RF01 e RF02, solicitante:** entre com e-mail e senha. Abra um chamado sintético, por exemplo “Falha de acesso à rede”, com descrição e categoria Rede. Mostre protocolo, status Aberto e prioridade Média na confirmação/detalhe.
3. **RF03, solicitante:** abra Meus chamados. Aplique filtros de status e categoria, limpe-os e consulte o detalhe. Mostre o histórico vazio se o chamado ainda não tem ações registradas. A paginação aparece quando existem mais de dez registros visíveis; não simule controles ausentes.
4. **RF01 e RF04, técnico:** saia da conta e entre como técnico. Localize o chamado, altere a prioridade para Alta e selecione Iniciar atendimento. Mostre que cada ação tem sua confirmação.
5. **RF05, técnico:** registre uma anotação, como “Configuração de rede verificada; equipamento em teste”. Mostre a linha do tempo, a autoria, a data UTC e a mudança de Aberto para Em atendimento. Explique que anotações são somente de inclusão.
6. **RF04, conclusão:** tente concluir com solução composta só por espaços e mostre a orientação de correção. Informe uma solução válida e conclua. Mostre solução, data UTC, evento e ausência dos controles de prioridade/status. Uma anotação posterior é permitida e não reabre o chamado.
7. **RF06, técnico:** abra Indicadores e apresente os agrupamentos por status e prioridade, inclusive zeros. As contagens representam chamados; incluir anotações não acrescenta chamados ao painel.
8. **RF05 e permissões, solicitante:** saia, volte ao solicitante e consulte o histórico do próprio chamado, com solução e registros do técnico. Mostre a ausência do formulário de anotações. O endereço `/indicadores` deve apresentar acesso negado para esse perfil. Um segundo solicitante não pode acessar o detalhe do primeiro.
9. **Fechamento:** apresente o PDF e o Kanban como acompanhamento das tarefas do desenvolvimento, separado do atendimento. Confira o checklist do LEX. Só registre gravação, apresentação e postagem como realizadas depois de executá-las.

## Revisão e retrospectiva técnica

A revisão final compara as seis funcionalidades com os fluxos dos dois perfis, os registros persistidos e os diagramas. A implementação manteve o histórico de status da Sprint 2 e acrescentou anotações sem reconstruir eventos ausentes. As contagens consultam chamados sem juntá-los ao histórico, evitando multiplicação dos totais.

A revisão da interface encontrou uma repetição do histórico no título HTML. A correção recebeu teste específico e foi conferida novamente no navegador. O trabalho reforçou a necessidade de comparar o documento, os desenhos e a aplicação renderizada, além de conferir a execução. Gravação, apresentação e avaliação acadêmica não são substituídas por essa revisão técnica.
