# slide-hustle agent instructions

## On every session, read in this order:

1. `BRAND.md`
2. `FRAMEWORK.md`
3. The brief specified by the user

## Rules

- Never change watermark size (`108px`) or position (`top: 86px`, `left: -10px`).
- Claude and Claude Code mentions always use `#D97757`.
- Databricks mentions always use `#FF8C00`.
- Red background means maximum one slide per carousel.
- `templates/slide-hustle.css` is read-only unless the user explicitly asks to change the design system.
- After generating `slides.html`, always run `export.py` automatically.
- If asked to fix slide N, only re-export slide N.
- Output folder equals the brief `meta.output` value.

## Token Efficiency Rules

- CSS lives in `templates/slide-hustle.css`; never inline it in `slides.html`.
- Use template partials from `templates/`; do not write slide HTML from scratch.
- Confirm output files after export before reporting done.

## Brief Parsing

- Read briefs as YAML.
- Map icon names to SVG from `icons/library.md`.
- Apply background colors from `BRAND.md` color tokens.
- Inject content into the correct partial template.

