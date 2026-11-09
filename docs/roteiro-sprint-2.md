# Preparação da apresentação da Sprint 2

## Roteiro

1. Iniciar com `docker compose up -d`, acessar localhost:8080 e consultar as credenciais pelo comando `docker compose exec app flask demo-credentials`. As senhas ficam restritas ao terminal local.
2. Entrar como solicitante. Abrir um chamado com dados sintéticos e conferir protocolo, status Aberto e confirmação. Acessar Meus chamados e o detalhe, que mostra prioridade Média.
3. Combinar filtros de status e categoria, limpar os filtros e mostrar uma combinação sem resultados. Se houver mais de dez registros visíveis, navegar para a próxima página e conferir a manutenção dos filtros.
4. Sair e entrar como técnico. Consultar os chamados, abrir o detalhe e definir prioridade Alta. Mostrar que prioridade e status são ações separadas.
5. Iniciar o atendimento. Tentar concluir informando apenas espaços na solução e conferir a rejeição. Informar uma solução válida e concluir. Conferir solução, conclusão UTC e ausência de controles de edição no chamado concluído.
6. Voltar ao perfil solicitante e consultar o resultado. Explicar a restrição aos próprios chamados; a tentativa de consultar registros alheios e as alterações não autorizadas foram verificadas com contas temporárias nos testes.
7. Abrir o quadro do projeto e distinguir tarefas de desenvolvimento dos chamados. Apresentar UC01 a UC07 e localizar no código uma função de cada sequência. Mostrar as associações e operações de Ticket, User e StatusEvent e o fluxo de atividades.
8. Delimitar a próxima entrega: a interface de histórico, as anotações e o painel de indicadores pertencem à Sprint 3. Os eventos automáticos de status já são persistidos nesta Sprint.

## Revisão e retrospectiva técnica

A revisão comparou RF03 e RF04 com as permissões, os formulários, a migração, os testes e o fluxo no navegador. A consulta respeita a propriedade antes dos filtros, e o atendimento grava os eventos na mesma transação da mudança de status. As funções de módulo foram mantidas como funções, sem criar controllers fictícios nos desenhos.

O primeiro ensaio encontrou um problema nos valores iniciais dos filtros opcionais. A correção passou a distinguir a opção vazia dos valores inválidos. A migração e as falhas de persistência também foram verificadas com estado temporário, evitando usar os dados de demonstração como massa de teste.

A revisão dos diagramas exigiu conferir responsabilidades e chamadas, além da renderização. Na exportação, foi necessário respeitar a orientação das páginas e ampliar o limite de imagens do renderizador para evitar recorte. Na próxima Sprint, os eventos existentes poderão alimentar o histórico, mantendo a mesma verificação de propriedade da consulta.

O roteiro está preparado. A apresentação ao professor e a avaliação acadêmica não foram realizadas por esta implementação.
