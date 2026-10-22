# Verificações da Sprint 1

Resultados de execução real nesta implementação. Testes não usam os dados de demonstração. Containers e volumes de ensaio pertencem ao projeto isolado `helpdesk-sprint1-check`; nenhum volume foi apagado.

| Verificação | Evidência |
|---|---|
| Migração inicial em banco vazio | Alembic gerou/aplicou `3c65b6acc942`; `flask db check` não encontrou operações adicionais |
| Compose | `docker compose config --quiet` passou |
| Imagem e inicialização | Build e inicialização isolada passaram. Exportação limpa por `git archive` (sem clonar novamente, banco, segredos ou runtime) iniciou com o comando exato `docker compose up -d`, volume próprio e aplicação healthy em 127.0.0.1:8080 |
| Usuário e permissões | `id` retornou UID/GID 10001 (helpdesk); banco, chave e credenciais iniciais em modo 0600 |
| Saúde HTTP | GET `/healthz` retornou 200 e `{"status":"ok"}` |
| Testes isolados | 43 testes passaram sem warnings, usando configuração real e banco/estado temporários. Após consolidar o catálogo final, os cinco testes de seed/Kanban passaram novamente |
| Falha de migração | Container descartável com revisão Alembic inválida saiu com erro; Gunicorn não foi iniciado |
| Navegador Chromium/Playwright 1.64.1 | Login dos dois perfis, abertura, confirmação, atualização GET, logout, bloqueio anônimo e movimento Kanban passaram |
| Acessibilidade automatizada | axe-core/playwright 4.11.1: nenhuma violação WCAG A/AA nos escopos executados de login, início solicitante, abertura, confirmação, início técnico e quadro |
| Responsividade | Sem overflow horizontal em 320, 390, 768 e 1440px; capturas full page em 390/1440px |
| Persistência | Após `up -d --force-recreate --wait`, mesmo chamado, sessão anterior, credenciais e coluna Kanban continuaram disponíveis; coluna original restaurada. Repetido com sucesso na exportação limpa e no catálogo final |
| Diagramas | Quatro fontes renderizadas com PlantUML 1.2025.10 em SVG/PNG; quatro PNGs abertos e inspecionados, sem cortes ou sobreposição |

## Correção encontrada durante a verificação

O navegador encontrou erro no prazo CSRF: Flask-WTF1.3.0 requer segundos nessa configuração. O valor `timedelta` foi substituído por 28.800 segundos e as fixtures passaram a carregar a configuração real, isolando apenas o diretório/banco. Depois da correção, testes e fluxo real passaram. Também foi removida a API obsoleta `get_engine()` do ambiente Alembic; execução sem warnings.

## Alcance da revisão visual

Foram inspecionadas capturas de login, páginas iniciais por perfil, formulário, confirmação e quadro, em desktop/celular. Foco do link “Pular para o conteúdo” foi verificado por teclado. Labels, alvos, estados, textos e componentes foram revisados nas capturas e nos fluxos do navegador.

Contraste renderizado foi verificado pelo axe. O CSS foi formatado para leitura; a equivalência das regras antes/depois foi confirmada pelo parser CSS do Chromium. A revisão considera a interface de ferramenta interna e o sistema visual registrado em DESIGN.md.

## Limitações e pendências reais

- Revisão de navegador em Chromium headless com viewports emulados; nenhum aparelho físico, Safari/Firefox ou leitor de tela foi usado. Não se declara certificação WCAG.
- Sem testes de carga, publicação HTTPS, recuperação de backup ou validação em outro sistema operacional. A configuração de Secure foi testada; TLS não foi implantado nesta entrega local.
- RF03–RF06 permanecem no backlog. A página do chamado apenas confirma a abertura do próprio solicitante.
- As contas e a recuperação de senhas são de demonstração local; publicação real exige ajustes descritos no README.
- CI está versionada e o primeiro push acionou o workflow, mas nenhum step foi executado: GitHub informou “The job was not started because your account is locked due to a billing issue.” [Execução bloqueada](https://github.com/Lfijho/chamadosLES/actions/runs/39865825032). O usuário precisa regularizar a conta para permitir execução remota; não se declara CI aprovada.
- Primeiro bloco commitado e enviado como `86ac70b` em `feature/sprint-1-helpdesk`, com autor e committer Leandro Pinzon Filho <leandro.pinzon.filho@gmail.com>. Documentação, UML e acompanhamento consolidados em segundo bloco, com a mesma identidade. A branch principal não recebeu commits ou merge.

Os containers isolados de verificação foram encerrados com `down`, sem remover volumes. A aplicação normal do repositório foi iniciada separadamente com `docker compose up -d`, ficou healthy e respondeu 200 em `/healthz`, para uso com os comandos do README. O seed final criou duas contas e 14 tarefas: sete concluídas, uma em andamento (CI remota) e seis futuras no Backlog.
