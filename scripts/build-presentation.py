#!/usr/bin/env python3
"""Gera o HTML autônomo e o roteiro a partir de uma única fonte de conteúdo."""
from pathlib import Path
import base64
import html
import json
import mimetypes
import re

ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / "docs/apresentacao"


def asset_url(name):
    path = (SOURCE / name).resolve()
    path.relative_to(ROOT / "docs")
    mime = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
    return "data:" + mime + ";base64," + base64.b64encode(path.read_bytes()).decode("ascii")


def resolve_assets(content):
    def replace(match):
        kind, name = match.groups()
        if kind == "asset":
            return asset_url(name)
        if kind == "diagram":
            src = asset_url("../diagrams/apresentacao/" + name + ".svg")
            label = "Diagrama " + name.replace("-", " ")
            return (f'<button class="diagram-button" aria-label="Ampliar {html.escape(label)}">'
                    f'<img src="{src}" alt="{html.escape(label)}"></button>')
        return f'<img src="{asset_url(name)}" alt="{html.escape(Path(name).stem)}">'
    return re.sub(r"\{\{(asset|image|diagram):([^}]+)\}\}", replace, content)


def timestamp(seconds):
    return f"{seconds // 60:02d}:{seconds % 60:02d}"


def main():
    deck = json.loads((SOURCE / "slides.json").read_text())
    assert len(deck["slides"]) == 16
    assert sum(slide["seconds"] for slide in deck["slides"]) == 600
    fonts = []
    for weight in (400, 600, 800):
        fonts.append("@font-face{font-family:Manrope;font-style:normal;font-weight:"
                     + str(weight) + ";font-display:swap;src:url("
                     + asset_url(f"assets/manrope-{weight}.ttf") + ") format('truetype');}")
    sections, notes = [], []
    script = ["# HelpDesk — roteiro dos slides (10 minutos)", "",
              "Leandro Pinzon Filho · Laboratório de Engenharia de Software · Sprint 3", "",
              "A duração de 10 minutos atende ao planejamento desta apresentação; não é um limite informado no trecho da atividade. "
              "A contextualização é breve, pois as Sprints 1 e 2 já foram apresentadas. O foco são RF05, RF06 e as atualizações da modelagem.", "",
              "Abra [os slides](../apresentacao-helpdesk.html) no navegador. Use **F** para tela cheia, "
              "setas ou Espaço para avançar e **N** para consultar estas notas. As notas aparecem na mesma tela: mantenha-as fechadas durante o compartilhamento. "
              "Cada intervalo abaixo é um tempo sugerido; os slides não avançam automaticamente.", "",
              "Prepare a aplicação antes, caso substitua as capturas por uma demonstração. Use somente dados de ensaio e nunca mostre a saída das credenciais na gravação.", ""]
    elapsed = 0
    for index, slide in enumerate(deck["slides"], 1):
        range_ = timestamp(elapsed) + "–" + timestamp(elapsed + slide["seconds"])
        elapsed += slide["seconds"]
        title, section = map(html.escape, (slide["title"], slide["section"]))
        header = "" if slide["kind"] in ("title", "closing") else f'<div class="eyebrow reveal" data-edit>{section}</div><h2 class="reveal" data-edit>{title}</h2>'
        if slide["kind"] == "closing":
            header = f'<div class="eyebrow reveal" data-edit>{section}</div>'
        footer = f'<footer class="slide-footer"><span>HelpDesk · Leandro Pinzon Filho</span><span>{index:02d} / 16</span></footer>'
        sections.append(f'<section class="slide {slide["kind"]}'+ (' active visible' if index == 1 else '')
                        + f'" id="slide-{index}" aria-label="{index}. {title}" aria-hidden="{str(index != 1).lower()}"'
                        + (' inert' if index != 1 else '') + '>' + header
                        + resolve_assets(slide["body"]) + footer + '</section>')
        notes.append(dict(title=slide["title"], range=range_, notes=slide["notes"], action=slide["action"]))
        script.extend([f'## {range_} · Slide {index:02d} — {slide["title"]}', "",
                       "**Fala sugerida**", "", slide["notes"], "", "**Na tela:** " + slide["action"], ""])
    output = (SOURCE / "modelo.html").read_text()
    output = output.replace("{{FONTS}}", "\n".join(fonts)).replace("{{SLIDES}}", "\n".join(sections))
    output = output.replace("{{NOTES_JSON}}", json.dumps(notes, ensure_ascii=False).replace("</", "<\\/"))
    assert not re.search(r"\{\{[^}]+\}\}", output), "Marcador não resolvido"
    (ROOT / "docs/apresentacao-helpdesk.html").write_text(output)
    (SOURCE / "roteiro-10-minutos.md").write_text("\n".join(script))
    print("HTML e roteiro gerados: 16 slides, 600 segundos, recursos incorporados.")


if __name__ == "__main__":
    main()
