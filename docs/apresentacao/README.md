# Apresentação do HelpDesk — 10 minutos

Leandro Pinzon Filho · Laboratório de Engenharia de Software · entrega final de 03/12/2026.

- [Slides no navegador](../apresentacao-helpdesk.html): 16 slides em 16:9, com fontes, imagens e diagramas incorporados. Baixe o HTML e abra em Chrome, Edge ou Firefox; não exige servidor nem conexão com a internet.
- [PDF dos slides](../apresentacao-helpdesk.pdf): uma página por slide, gerada do mesmo HTML.
- [Roteiro cronometrado](roteiro-10-minutos.md): intervalos contínuos de 00:00 a 10:00, falas sugeridas e indicações do que apontar na tela.

A apresentação contextualiza o sistema e as três Sprints e se concentra nas atualizações da Sprint 3: RF05, RF06, requisitos, especificações e modelagem. As Sprints 1 e 2 já foram apresentadas. O planejamento de 10 minutos é uma escolha desta apresentação, não um limite definido no trecho da atividade.

## Apresentar e editar

Use setas, Espaço ou Page Down/Page Up para navegar; Home/End vão ao início/fim. Também há navegação por deslize e roda do mouse. **F** ativa tela cheia. Os controles aparecem ao mover o ponteiro ou receber foco de teclado.

**N** mostra o roteiro e o intervalo do slide atual. As notas aparecem na mesma janela: mantenha-as fechadas ao compartilhar a tela. Não há avanço automático. Clique nos diagramas para ampliar; o botão do slide 5 abre o caso de uso completo UC01–UC10. Esc fecha a ampliação.

Para editar os textos, pressione **E** ou use o botão no canto superior esquerdo. Clique no texto, altere e pressione Esc para sair da edição. As alterações ficam no armazenamento local do navegador; **Ctrl+S** ou **Cmd+S** baixa uma cópia do HTML. Essa edição não altera o PDF ou as fontes versionadas: para manter todos os arquivos coerentes, atualize a fonte e regenere-os.

As capturas mostram dados de ensaio da aplicação existente. Não contêm credenciais. Para uma demonstração ao vivo, prepare as sessões antes e substitua o bloco do slide 7 pelo mesmo fluxo, sem acrescentar tempo. Gravação, apresentação e postagem no LEX continuam pendentes até serem realizadas.

## Conteúdo e diagramas

`slides.json` é a fonte do conteúdo, das notas e dos tempos. `modelo.html` define o visual e os controles. A licença da fonte Manrope acompanha os arquivos em `assets/`.

Os desenhos de projeção estão em [../diagrams/apresentacao/](../diagrams/apresentacao/), com fontes PlantUML e imagens SVG/PNG. São recortes identificados dos fluxos da Sprint 3: casos de uso UC08–UC10, sequências de histórico/anotação/indicadores, classes centrais e atividades de consulta/anotação. A sequência de anotação apresenta a validação do formulário e o caminho de inclusão sem falha de persistência. Atributos e operações do diagrama de classes foram selecionados para leitura em projeção.

O diagrama de atividades foi dividido em duas partes conectadas por A. As três raias distinguem solicitante, HelpDesk e técnico; as decisões e junções permitem consultar o histórico e optar por anotar, corrigir ou cancelar. Os documentos e diagramas completos das Sprints anteriores e da entrega consolidada permanecem preservados em [entrega-sprint-3.pdf](../entrega-sprint-3.pdf).

## Regenerar

Na raiz do repositório, com Python 3 para gerar o HTML e o roteiro:

```bash
python3 scripts/build-presentation.py
```

Para regenerar somente as figuras desta apresentação com o renderizador opcional do projeto:

```bash
./scripts/render-diagrams.sh -nbthread 1 'apresentacao/*.puml'
python3 scripts/build-presentation.py
```

Para exportar novamente o PDF, use a impressão do navegador, com fundos ativados e sem cabeçalhos/rodapés do navegador, ou a automação opcional abaixo. Node e Playwright são ferramentas dessa exportação, não requisitos para apresentar ou iniciar a aplicação:

```bash
npm install --prefix /tmp/helpdesk-browser playwright@1.64.1
NODE_PATH=/tmp/helpdesk-browser/node_modules /tmp/helpdesk-browser/node_modules/.bin/playwright install chromium
NODE_PATH=/tmp/helpdesk-browser/node_modules node scripts/export-presentation.cjs
```

O exportador bloqueia requisições HTTP e imprime o HTML local em 16 páginas. Nenhum desses comandos acessa o banco de demonstração. Após mudanças de conteúdo ou layout, confira novamente a leitura, as imagens e a distribuição dos tempos.
