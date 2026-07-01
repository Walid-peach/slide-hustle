from __future__ import annotations

import argparse
import asyncio
import html
import re
from pathlib import Path

import yaml

from export import assemble_pdf, existing_slide_paths, export_slides


ROOT = Path(__file__).resolve().parent
TEMPLATES = ROOT / "templates"
ICONS = ROOT / "icons" / "library.md"
OUTPUT = ROOT / "output"


def load_icons() -> dict[str, str]:
    text = ICONS.read_text(encoding="utf-8")
    icons: dict[str, str] = {}
    pattern = re.compile(r"<!--\s*(?P<name>[\w-]+)\s*-->\s*```svg\s*(?P<svg>.*?)\s*```", re.S)
    for match in pattern.finditer(text):
        icons[match.group("name")] = match.group("svg").strip()
    return icons


def esc(value: object) -> str:
    return html.escape(str(value or ""), quote=True)


def accent(text: str) -> str:
    text = esc(text)
    text = re.sub(r"\b(Claude Code|Claude)\b", r'<span class="accent-claude">\1</span>', text)
    text = re.sub(r"\b(Databricks)\b", r'<span class="accent-databricks">\1</span>', text)
    return text


def render_content(slide: dict) -> str:
    pieces: list[str] = []
    title = slide.get("title")
    heading = slide.get("heading")
    subtitle = slide.get("subtitle")

    if title:
        pieces.append(f"<h1>{accent(title)}</h1>")
    if heading:
        pieces.append(f"<h2>{accent(heading)}</h2>")
    if subtitle:
        pieces.append(f'<p class="subtitle">{accent(subtitle)}</p>')

    content = slide.get("content") or {}
    content_type = content.get("type")

    if content_type == "bullets":
        pieces.append(render_bullets(content.get("items", [])))
    elif content_type == "bullets+box":
        pieces.append(render_bullets(content.get("items", [])))
        pieces.append(f'<div class="insight-box">{accent(content.get("box", ""))}</div>')
    elif content_type == "quote":
        pieces.append(f'<blockquote class="quote">{accent(content.get("text", ""))}</blockquote>')
    elif content_type == "code":
        pieces.append(f'<pre class="code-block">{esc(content.get("code", ""))}</pre>')
    elif content_type == "agents":
        pieces.append(render_agents(content.get("items", [])))
    elif content_type == "stats":
        pieces.append(render_stats(content.get("items", [])))
    elif content_type == "cta":
        pieces.append(f'<p class="body">{accent(content.get("command", ""))}</p>')
        pieces.append(render_bullets(content.get("items", [])))
        pieces.append(f'<p class="question">{accent(content.get("question", ""))}</p>')

    if slide.get("verdict"):
        pieces.append(f'<p class="verdict">{accent(slide["verdict"])}</p>')

    return "\n    ".join(piece for piece in pieces if piece)


def render_bullets(items: list[object]) -> str:
    lis = "\n".join(f"<li>{accent(str(item))}</li>" for item in items)
    return f'<ul class="bullets">\n{lis}\n</ul>'


def render_agents(items: list[dict]) -> str:
    rows = []
    for item in items:
        rows.append(
            '<div class="agent-pill">'
            f'<strong>{accent(item.get("name", ""))}</strong> '
            f'{accent(item.get("description", ""))}'
            "</div>"
        )
    return '<div class="agents">' + "\n".join(rows) + "</div>"


def render_stats(items: list[dict]) -> str:
    rows = []
    for item in items:
        rows.append(
            '<div class="stat">'
            f'<strong>{accent(item.get("value", ""))}</strong>'
            f'<span>{accent(item.get("label", ""))}</span>'
            "</div>"
        )
    return '<div class="stats">' + "\n".join(rows) + "</div>"


def apply_template(template: str, values: dict[str, str]) -> str:
    for key, value in values.items():
        template = template.replace("{{" + key + "}}", value)
    return template


def render_deck(brief: dict) -> tuple[str, Path]:
    icons = load_icons()
    slides = sorted(brief.get("slides", []), key=lambda slide: slide.get("id", 0))
    meta = brief.get("meta", {})
    output_name = meta.get("output", "carousel")
    output_dir = OUTPUT / output_name
    output_dir.mkdir(parents=True, exist_ok=True)

    red_count = sum(1 for slide in slides if slide.get("bg") == "red")
    if red_count > 1:
        raise ValueError("Brand rule violation: only one red slide is allowed.")

    rendered_slides = []
    total = str(len(slides))
    for slide in slides:
        bg = slide.get("bg", "ivory")
        template_path = TEMPLATES / f"slide-{bg}.html"
        if not template_path.exists():
            raise ValueError(f"Unknown slide background: {bg}")

        icon_name = slide.get("icon")
        icon = icons.get(icon_name, "") if icon_name else ""
        if icon_name and not icon:
            raise ValueError(f"Unknown icon: {icon_name}")

        rendered_slides.append(
            apply_template(
                template_path.read_text(encoding="utf-8"),
                {
                    "id": esc(slide.get("id", "")),
                    "total": total,
                    "watermark": esc(slide.get("watermark", "")),
                    "icon": icon,
                    "main": render_content(slide),
                    "swipe": '<p class="swipe">Swipe -></p>' if slide.get("swipe") else "",
                },
            )
        )

    html_doc = f"""<!doctype html>
<html lang="{esc(meta.get("language", "EN")).lower()}">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{esc(meta.get("topic", "Carousel"))}</title>
  <link rel="stylesheet" href="../../templates/slide-hustle.css">
</head>
<body>
  <div class="deck">
    {"".join(rendered_slides)}
  </div>
</body>
</html>
"""
    return html_doc, output_dir


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate deck HTML from a YAML brief.")
    parser.add_argument("brief", type=Path, help="Path to the YAML brief.")
    args = parser.parse_args()

    brief = yaml.safe_load(args.brief.read_text(encoding="utf-8"))
    html_doc, output_dir = render_deck(brief)
    slides_html = output_dir / "slides.html"
    slides_html.write_text(html_doc, encoding="utf-8")
    print(f"Generated {slides_html}")

    exported = asyncio.run(export_slides(slides_html))
    pdf_path = output_dir / f"{output_dir.name}.pdf"
    assemble_pdf(existing_slide_paths(output_dir), pdf_path)
    print(f"Exported {len(exported)} slide(s) and {pdf_path}")


if __name__ == "__main__":
    main()

