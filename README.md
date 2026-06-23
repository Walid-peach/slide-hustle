# Slide Hustle

> A tiny agentic content kitchen that turns Obsidian notes into LinkedIn slide decks.
> Write the brief. The agent handles the rest.

Built by [Walid El Khoukh](https://linkedin.com/in/walid-elkhoukh) · Cloud Data Engineer

## What Is This?

`slide-hustle` is an agentic pipeline that takes a structured brief from your Obsidian vault and generates a fully designed, export-ready LinkedIn carousel. The name is a wink: serious output, slightly unserious production energy.

```text
Obsidian note -> Claude Code agent -> PNG slides -> LinkedIn
```

You write the content. The agent applies the design system, generates HTML, exports PNGs, and assembles the PDF.

## Quick Start

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
playwright install chromium

cp briefs/_template.yaml briefs/my-post.yaml
python generate.py briefs/my-post.yaml
python export.py output/slide_hustle_example/slides.html

# or run the example in one shot
make example
```

Or ask Claude Code:

```bash
claude "Generate deck from briefs/my-post.yaml"
```

## Project Structure

```text
slide-hustle/
├── BRAND.md
├── FRAMEWORK.md
├── CLAUDE.md
├── README.md
├── requirements.txt
├── generate.py
├── export.py
├── templates/
│   ├── slide-navy.html
│   ├── slide-ivory.html
│   ├── slide-red.html
│   └── slide-hustle.css
├── icons/
│   └── library.md
├── briefs/
│   ├── _template.yaml
│   ├── slide-hustle-launch.yaml
│   ├── claude-code-post.yaml
│   ├── subagents-post.yaml
│   ├── databricks-aitools.yaml
│   └── remotion-post.yaml
└── output/
```

## Brief Format

```yaml
meta:
  topic: "Claude Code Subagents"
  language: EN
  slides: 7
  output: "slide_hustle_subagents"

slides:
  - id: 1
    bg: navy
    watermark: "SUBAGENTS"
    title: "Subagents Claude Code in Data Engineering."
    subtitle: "Here is what changes."
    swipe: true
```

## Outputs

Run `make example` to generate the bundled sample deck from `briefs/_template.yaml`.

Each run creates:

- `output/<meta.output>/slides.html`
- `output/<meta.output>/slide_01.png` through `slide_N.png`
- `output/<meta.output>/<meta.output>.pdf`

## Design System

All slides use the same fixed brand rules:

- Size: `1080 x 1080px`
- Padding: `88px`
- Font: Syne
- Bottom bar: `AI · Data Engineering · 2026`
- Slide 1: navy hook slide
- Slide 5: red impact slide, maximum one per carousel
- Last slide: ivory CTA

See [BRAND.md](BRAND.md) and [FRAMEWORK.md](FRAMEWORK.md) for the full rules.

