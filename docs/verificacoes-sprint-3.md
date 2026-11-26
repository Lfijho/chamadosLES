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

A operação CLI também criou uma cópia privada no volume de teste. O procedimento completo está em [backup-restauracao.md](backup-restauracao.md). Gravação de vídeo, apresentação e publicação no LEX permanecem pendentes.


## Fechamento da validação

A instância existente foi atualizada com `docker compose up -d --build --wait`, seguida de `docker compose up -d`, e ficou saudável em `http://localhost:8080`. Antes da migração foi criado um snapshot privado pela API do SQLite. Uma comparação de conteúdo antes/depois confirmou preservação integral de chamados, eventos, usuários, tarefas, chave de sessão e credenciais. A comparação não publicou conteúdo sensível.

Uma árvore limpa do commit de implementação, exportada por `git archive` sem estado local, iniciou pelo Compose no projeto `helpdesk-sprint3-clean-check`. Foi usada a porta 8085 para evitar conflito com a instância de uso. Healthcheck e acesso HTTP foram aprovados. Isso verifica a inicialização sem dependências Python/Node no host; o comando padrão na instância normal foi conferido em 8080. O código da aplicação não mudou após esse bloco; os arquivos posteriores consolidam documentação, catálogo e ferramentas opcionais de entrega.

O bundle de teste foi criado com o comando de backup e cópia dos arquivos auxiliares com o serviço parado. A restauração em volume novo `helpdesk-restore-verified-check` passou: integridade, arquivos privados, healthcheck, login, chamado concluído, prioridade, solução, três anotações e dois eventos preservados. Uma segunda tentativa foi recusada por já existir estado, e a aplicação permaneceu saudável. O primeiro ensaio do auxiliar revelou que o serviço remove todas as capacidades; foram necessárias capacidades de arquivos explícitas no auxiliar de preparação. O comando documentado foi corrigido e o ensaio repetido em outro volume, sem apagar o anterior. O servidor normal permanece com usuário sem privilégios e sem capacidades adicionais.

A documentação final foi gerada da mesma fonte Markdown para DOCX e PDF, com 26 páginas numeradas. As 13 figuras UML ocupam 17 imagens por causa das continuações; fontes, SVG e PNG estão versionados. Foram conferidas as funções do código, a ordem das chamadas, guardas, retorno e ativação, associações e multiplicidades, a inclusão somente no ramo válido e a preservação das tabelas aprovadas dos casos anteriores. Todas as páginas do PDF foram abertas para inspeção de texto, tabelas, cortes e legibilidade. Os documentos e desenhos históricos das Sprints 1 e 2 permaneceram intactos. A prosa final foi revisada mantendo comandos, identificadores e fatos.

Roteiro do vídeo e checklist do LEX estão preparados. As tarefas de código, testes, documentação, revisão e validação têm aceite verificado. S3-12 permanece no Backlog: gravação, apresentação, revisão do vídeo e postagem ainda precisam ser realizadas pelo responsável. Não foram medidos desempenho sob carga ou uso com grandes históricos; avaliação com leitor de tela e dispositivos físicos não foi realizada. A aplicação continua configurada para demonstração local, conforme o README.


O catálogo final passou novamente nos quatro testes de sincronização. No quadro operacional de localhost:8080, o técnico atualizou 12 tarefas da Sprint 3 para Concluído e manteve S3-12 no Backlog. Duas execuções subsequentes do seed preservaram integralmente as colunas, as contas, chamados, eventos, anotações e arquivos de estado; não houve duplicação. Colunas das Sprints 1 e 2 foram preservadas.


## Revisão e retrospectiva técnica preservadas

A revisão final compara as seis funcionalidades com os fluxos dos dois perfis, os registros persistidos e os diagramas. A implementação manteve o histórico de status da Sprint 2 e acrescentou anotações sem reconstruir eventos ausentes. As contagens consultam chamados sem juntá-los ao histórico, evitando multiplicação dos totais.

A revisão da interface encontrou uma repetição do histórico no título HTML. A correção recebeu teste específico e foi conferida novamente no navegador. O trabalho reforçou a necessidade de comparar o documento, os desenhos e a aplicação renderizada, além de conferir a execução. Gravação, apresentação e avaliação acadêmica não são substituídas por essa revisão técnica.

O roteiro foi posteriormente corrigido a partir do trecho da atividade informado pelo responsável: o vídeo de 03/12 apresenta as atualizações da Sprint 3. As Sprints 1 e 2 já foram apresentadas. O roteiro cronometrado cobre RF05/RF06 e os artefatos documentais atualizados; 6min30 é uma sugestão, não uma duração exigida. O documento acadêmico consolidado e a implementação foram preservados.

## Apresentação de 10 minutos

Foram gerados `docs/apresentacao-helpdesk.html`, `docs/apresentacao-helpdesk.pdf` e o roteiro em `docs/apresentacao/roteiro-10-minutos.md`, com 16 intervalos contínuos totalizando 600 segundos. O conteúdo vem de `slides.json`; o PDF é exportado do HTML. As sete fontes PlantUML de projeção receberam SVG e PNG; a renderização também foi repetida em diretório temporário vazio, produzindo os 14 arquivos. Os desenhos completos já entregues foram preservados.

A conferência no Chromium percorreu os 16 slides em 1280×720: uma seção ativa por vez, imagens carregadas, ausência de conteúdo fora do palco e nenhum erro JavaScript ou pedido HTTP. O PDF foi renderizado em 16 páginas 16:9 e inspecionado visualmente, incluindo a leitura das sequências e dos recortes de atividades. Em 390×844, o palco manteve 390×219,375 pixels, preservando 16:9 com margens, sem reorganizar o conteúdo.

Também foram verificados teclas de navegação, roteiro, abertura/ampliação de diagramas, diagrama completo UC01–UC10, navegação por roda e deslize, edição com persistência local e download do HTML editado. Uma cópia do HTML foi aberta isoladamente em `/tmp`, com requisições HTTP bloqueadas; fontes e imagens continuaram disponíveis. As capturas e relatórios temporários estão em `artifacts/slides/`, ignorado no Git.

A mudança envolve apresentação, fontes de figuras e documentação. Não foi executada nova regressão da aplicação neste bloco, nem foram alterados código, migrações, dados ou documentos acadêmicos anteriores. A inspeção ocorreu em Chromium; outros navegadores e o projetor da apresentação não foram verificados. O roteiro não foi cronometrado com uma fala real do apresentador. Gravação, apresentação e postagem permanecem pendentes.
