---
name: HelpDesk
description: Ferramenta interna de suporte com formulários claros e operação previsível.
colors:
  "ink": "#18353e"
  "muted": "#50656b"
  "canvas": "#f3f6f5"
  "surface": "#fff"
  "line": "#cbd7d5"
  "accent": "#126759"
  "accent-hover": "#0b5146"
  "tint": "#e6f2ed"
  "error": "#922c26"
  "error-bg": "#fff1ee"
  "focus": "#ae510b"
  "field-border": "#839c9a"
  "board-column": "#e7edeb"
  "selection": "#c4e6da"
typography:
  "headline":
    fontFamily: "\"Segoe UI\", Roboto, \"Helvetica Neue\", sans-serif"
    fontSize: "2rem"
    fontWeight: 700
    lineHeight: 1.2
    letterSpacing: "-.025em"
  "title":
    fontFamily: "\"Segoe UI\", Roboto, \"Helvetica Neue\", sans-serif"
    fontSize: "1.35rem"
    fontWeight: 700
    lineHeight: 1.3
  "subheading":
    fontFamily: "\"Segoe UI\", Roboto, \"Helvetica Neue\", sans-serif"
    fontSize: "1.05rem"
    fontWeight: 700
    lineHeight: 1.4
  "body":
    fontFamily: "\"Segoe UI\", Roboto, \"Helvetica Neue\", sans-serif"
    fontSize: "1rem"
    fontWeight: 400
    lineHeight: 1.55
  "label":
    fontFamily: "\"Segoe UI\", Roboto, \"Helvetica Neue\", sans-serif"
    fontSize: "1rem"
    fontWeight: 650
    lineHeight: 1.55
  "button":
    fontFamily: "\"Segoe UI\", Roboto, \"Helvetica Neue\", sans-serif"
    fontSize: ".95rem"
    fontWeight: 650
    lineHeight: 1.5
  "helper":
    fontFamily: "\"Segoe UI\", Roboto, \"Helvetica Neue\", sans-serif"
    fontSize: ".875rem"
    fontWeight: 400
    lineHeight: 1.55
rounded:
  "control": "6px"
  "notice": "8px"
  "panel": "12px"
  "status": "20px"
spacing:
  "6": "6px"
  "8": "8px"
  "10": "10px"
  "12": "12px"
  "16": "16px"
  "20": "20px"
  "24": "24px"
  "32": "32px"
  "48": "48px"
  "64": "64px"
components:
  "button-primary":
    backgroundColor: "{colors.accent}"
    textColor: "{colors.surface}"
    rounded: "{rounded.control}"
    typography: "{typography.button}"
    padding: "10px 20px"
  "button-primary-hover":
    backgroundColor: "{colors.accent-hover}"
  "button-secondary":
    backgroundColor: "{colors.surface}"
    textColor: "{colors.ink}"
    rounded: "{rounded.control}"
    typography: "{typography.button}"
    padding: "10px 20px"
  "button-quiet":
    backgroundColor: "transparent"
    textColor: "{colors.ink}"
    rounded: "{rounded.control}"
    typography: "{typography.button}"
    padding: "8px 14px"
  "input":
    backgroundColor: "{colors.surface}"
    textColor: "{colors.ink}"
    rounded: "{rounded.control}"
    typography: "{typography.body}"
    padding: "10px 12px"
    width: "100%"
  "nav-link":
    textColor: "{colors.muted}"
    rounded: "{rounded.control}"
    padding: "10px 12px"
  "nav-link-current":
    backgroundColor: "{colors.tint}"
    textColor: "{colors.accent}"
  "status":
    backgroundColor: "{colors.tint}"
    textColor: "{colors.accent}"
    rounded: "{rounded.status}"
    padding: "5px 12px"
  "panel":
    backgroundColor: "{colors.surface}"
    textColor: "{colors.ink}"
    rounded: "{rounded.panel}"
    padding: "32px"
  "notice-error":
    backgroundColor: "{colors.error-bg}"
    textColor: "{colors.error}"
    rounded: "{rounded.notice}"
    padding: "16px 20px"
  "notice-success":
    backgroundColor: "{colors.tint}"
    textColor: "{colors.accent}"
    rounded: "{rounded.notice}"
    padding: "16px 20px"
  "kanban-task":
    backgroundColor: "{colors.surface}"
    textColor: "{colors.ink}"
    rounded: "{rounded.panel}"
    padding: "20px"
---

# Design System: HelpDesk

## Overview

**Creative North Star: "Formulário institucional claro"**

A interface HelpDesk prioriza precisão, previsibilidade e conclusão de tarefas. A identidade aparece na tinta azul-esverdeada, na ação verde e nas superfícies brancas delimitadas por bordas suaves. Português do Brasil, orientações diretas e controles familiares sustentam o uso como ferramenta interna profissional.

Este registro consolida o CSS e os templates implementados na aplicação.

**Key Characteristics:**

- Hierarquia curta, com títulos legíveis e texto de apoio discreto.
- Superfícies planas, bordas explícitas e ações com alvos de pelo menos 44px.
- Formulários com labels persistentes, orientação e erro junto ao campo.
- Recursos locais, sem download de fontes, JavaScript ou CDN.

## Colors

A paleta combina neutros frios com verde funcional e cores específicas para erro e foco. Os valores normativos estão no frontmatter e correspondem a `helpdesk/static/app.css`.

### Primary

- **Verde de ação** (`accent`): links, botão principal e confirmação; `accent-hover` intensifica a ação no hover.
- **Verde de apoio** (`tint`): navegação ativa, hover secundário, avisos de sucesso e status.

### Neutral

- **Tinta azul-esverdeada** (`ink`): títulos, conteúdo e marca.
- **Texto secundário** (`muted`): orientação, metadados e textos auxiliares.
- **Fundo claro** (`canvas`) e **superfície branca** (`surface`): página e áreas de operação.
- **Linha suave** (`line`): painéis e divisores; **borda de campo** (`field-border`) torna controles distinguíveis.
- **Coluna do quadro** (`board-column`): base tonal sob os cartões; **seleção** (`selection`): destaque do texto selecionado.

O erro usa `error` sobre `error-bg`; o foco de teclado usa `focus`. São papéis semânticos, não acentos decorativos adicionais.

### Named Rules

**The Ação Clara Rule.** O verde identifica ações e confirmação; o erro combina texto explícito, borda e fundo próprios, sem depender apenas da cor.

## Typography

**Body Font:** Segoe UI, Roboto, Helvetica Neue e sans-serif, disponíveis localmente. A mesma família atende títulos e controles; não existe fonte de display ou mono distinta.

**Character:** leitura utilitária, títulos compactos e labels firmes. A base é 16px; a escala é fixa em rem, sem fonte externa.

### Hierarchy

- **Headline:** título de página; reduz para 1.75rem no celular.
- **Title / Subheading:** seções e cartões, com os papéis descritos no frontmatter.
- **Body:** conteúdo e campos; parágrafos limitados a 72ch quando o contêiner permite.
- **Label:** identificação persistente de campos, com peso intermediário.
- **Button:** ações de formulário e navegação por botão.
- **Helper:** dicas e erros de campo; avisos menores e metadados usam também .8rem, e metadados do quadro usam .75rem.

A introdução do login usa título de 2.7rem, entrelinha 1.15 e tracking -.03em, reduzido para 2rem no celular; é uma exceção daquela composição, não uma nova escala de display. Protocolo, contadores e código de erro usam algarismos tabulares.

### Named Rules

**The Hierarquia Funcional Rule.** Títulos descrevem a tarefa; labels permanecem visíveis e os textos auxiliares explicam o preenchimento.

## Layout

O contêiner comum tem largura máxima de 1200px e padding de 48px 24px 64px. Cabeçalho horizontal com marca, navegação e conta; rodapé discreto separado por linha. O formulário de chamado e sua orientação usam duas colunas na proporção 2:1, com intervalo de 64px. A página inicial usa 1.7:1 e o login 1.15:1.

Em até 1100px, os intervalos diminuem e o quadro passa de quatro para duas colunas. Em até 700px, formulários, orientação e quadro ficam em uma coluna; navegação ocupa uma nova linha, rodapé empilha e a página usa padding de 32px 20px 48px. A orientação da página inicial passa de divisor vertical a horizontal. Ações podem quebrar linha e ocupar a largura disponível.

O quadro tem largura máxima de 1480px, colunas com `minmax(0, 1fr)` e intervalo de 20px. A partir de 1500px, seu padding lateral é 32px. A escala de espaçamento registra os valores recorrentes; o CSS define exceções locais sem impor uma grade artificial.

## Elevation & Depth

A interface é plana: não há box-shadow. Fundo da página, superfície branca, fundo tonal do quadro e bordas de 1px estabelecem agrupamento e profundidade. O foco é contorno, não elevação.

### Named Rules

**The Superfície Plana Rule.** A separação entre áreas usa fundo, borda e espaço; não há sombras na implementação.

## Shapes

Controles têm cantos discretos; avisos usam arredondamento intermediário e painéis, formulários e cartões compartilham o raio maior. O status usa cápsula, enquanto o indicador de acesso do login é circular. Bordas contínuas delimitam campos e superfícies. Ícone da marca é SVG linear local.

## Components

### Buttons

Ação principal preenchida em verde, secundária branca com borda e ação discreta transparente. O padding e a tipografia estão no frontmatter; todos têm altura mínima de 44px. Hover altera fundo; `:active` desloca 1px no eixo vertical. O estado disabled tem opacidade .55 e cursor de espera. Não há transição animada.

### Inputs / Fields

Campos brancos com borda explícita, altura mínima de 46px e largura integral. Textarea redimensiona verticalmente e tem altura mínima de 180px. Labels persistem acima do campo; dicas e erros são associados por `aria-describedby`. Campo inválido usa borda de erro e mensagem escrita, além do resumo com `role="alert"`. A validação preserva valores não sensíveis.

O foco visível geral tem contorno de 3px e afastamento de 4px. O link de pular para o conteúdo aparece ao receber foco. `main` pode receber o destino desse link sem contorno visual adicional.

### Navigation

Links horizontais com alvos mínimos de 44px, peso 600 e padding confortável. Hover e `aria-current` usam fundo verde claro com texto de ação. No celular, a navegação passa para uma linha própria; o subtítulo da marca é ocultado já no breakpoint intermediário.

### Cards / Containers

Painéis brancos com borda suave e sem sombra. Formulário de chamado e resumo usam padding de 32px; login usa 36px e painel inicial 40px. No celular, esses painéis usam 24px. O resumo quebra títulos e protocolos longos; a descrição mantém as quebras digitadas.

### Status / Notices

Status é uma cápsula textual compacta, sem interação. Avisos de sucesso usam verde claro e `role="status"`; avisos de erro usam fundo próprio, texto de erro e `role="alert"`. Avisos aceitam quebra de conteúdo longo. Erros de página (400, 403, 404, 413 e 500) apresentam código, explicação e ação para retornar. Mensagens de credencial permanecem genéricas.

### Quadro acadêmico

Colunas tonais contêm títulos com contagem e cartões brancos com identificação, prioridade, aceite e formulário de movimento. Cada cartão usa padding de 20px e separação vertical de 16px. O destino após mover recebe contorno de 3px na cor de ação, com afastamento de 3px. Mover exige seletor e botão, sem depender de arrastar. Colunas vazias explicam como começar.

Na verificação de navegador, axe não apontou violações nas seis páginas auditadas e não houve overflow nos viewports de 320, 390, 768 e 1440px. Isso não substitui avaliação com tecnologia assistiva.

Não canonizado nem alterado: o `theme-color` legado do template base difere de `ink`; é metadado do navegador, não um token adicional de interface. As limitações da auditoria não são regras do sistema visual.

## Do's and Don'ts

### Do:

- **Do** reutilizar os tokens e os estados implementados, com português do Brasil direto e profissional.
- **Do** manter labels, associação de dicas e erros, foco visível e acesso por teclado.
- **Do** permitir quebra de protocolos, títulos e descrições longas, preservando a leitura em uma coluna no celular.
- **Do** conservar a distinção explícita entre o quadro acadêmico e os chamados de suporte.

### Don't:

- **Don't** substituir labels por placeholders nem comunicar erro apenas pela cor.
- **Don't** exigir arrastar para mover tarefas: mantenha seletor e botão acessíveis.
- **Don't** adicionar controles inativos para funções futuras, métricas ilustrativas ou elementos promocionais.
- **Don't** introduzir dependência de fontes remotas ou animações de entrada no fluxo atual.
