# Verificações da Sprint 3

## Implementação e regressão

Base: revisão documental validada da Sprint 2, incluindo RF01 a RF04. O histórico novo reutiliza StatusEvent e acrescenta TicketNote por uma migração aditiva. Não há preenchimento retroativo de eventos.

A suíte isolada passou com **104 testes** após as correções deste bloco. Inclui regressão das Sprints 1 e 2, autoria e data UTC das anotações, limite de 5.000 caracteres (inclusive texto Unicode), rejeição de espaços, CSRF, permissões de escrita/leitura, ordenação com empate, ausência de eventos inventados, imutabilidade do atendimento concluído, falha de persistência e contagens sem duplicação por histórico. A migração preserva integralmente as linhas de chamados, eventos, usuários e tarefas de uma base da Sprint 2. Há teste específico do título HTML para impedir repetição dos registros dentro da aba do navegador.

Comandos executados:

```bash
docker build --target test -t helpdesk-sprint3-tests .
docker run --rm helpdesk-sprint3-tests
docker compose config --quiet
```

O limite de corpo passou de 32 para 64 KiB para comportar formulários com até 5.000 caracteres Unicode codificados na requisição. Os limites dos campos continuam validados no servidor; o teste de tamanho excessivo usa o limite configurado. Os documentos históricos descrevem o comportamento da época de cada Sprint.

## Navegador e persistência isolados

Os projetos `helpdesk-sprint3-check` (porta 8083) e `helpdesk-sprint3-ui-check` (porta 8084) usam volumes próprios. Foram verificados login, logout, abertura, confirmação, consulta, prioridade, início, conclusão, anotações, histórico e indicadores. O ensaio inclui tentativa de escrita do solicitante e consulta por outro solicitante. Nenhum volume foi apagado.

O roteiro automatizado `scripts/sprint3-check.cjs` verificou oito estados: indicadores vazios e preenchidos; histórico vazio dos dois perfis; anotação inválida; atendimento em andamento; conclusão nos dois perfis. Axe não apontou violações nos escopos WCAG 2 A/AA e 2.1 AA executados. Não houve transbordamento horizontal em 320, 390, 768 e 1440 px. Esses resultados não garantem acessibilidade completa nem substituem avaliação com tecnologia assistiva ou aparelho físico.

A revisão visual identificou uma repetição do histórico no bloco do título. O template foi corrigido, a regressão recebeu um caso específico e os oito estados foram novamente verificados em um projeto novo. As capturas desktop/celular foram abertas e inspecionadas. A revisão posterior considerou resolvidas essa correção e a atualização da descrição do produto.

Após recriar o container sem remover volumes, persistiram o chamado concluído, a solução, prioridade Alta, três anotações, dois eventos de status e a coluna de uma tarefa do Kanban. As credenciais continuaram funcionando. O comando `flask demo-credentials` foi executado e validado sem divulgar seus valores.

O exame mecânico dos templates não resolveu a referência Jinja ao CSS. Os avisos de cor preta resultam dessa limitação; o navegador carregou os tokens reais. Avisos de tamanhos de fonte referem-se a regras preexistentes. As capturas e a verificação de navegador complementam essa limitação.

## Backup

`flask backup-db` usa a API de backup do SQLite e verifica integridade. Não copia diretamente o banco ativo. Arquivos de destino são criados exclusivamente, com modo 0600; o comando recusa sobrescrita e recusa o próprio banco como destino. Um teste restaura a cópia em outro arquivo temporário, confere integridade, chaves estrangeiras e todas as linhas das tabelas de negócio, usuários, tarefas e revisão.

A operação CLI também criou uma cópia privada no volume de teste. O procedimento de restauração e a validação final de inicialização constarão no fechamento da entrega. Gravação de vídeo, apresentação e publicação no LEX permanecem pendentes.
