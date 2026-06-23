# Carousel Framework

## Slide Anatomy

Every slide is a square card with:

- fixed dimensions: `1080 x 1080px`
- a large watermark behind content
- optional icon
- title or heading
- content block
- verdict or CTA
- bottom bar

## Supported Backgrounds

- `navy`
- `ivory`
- `red`

Each background maps to one partial in `templates/`.

## Supported Content Blocks

| Type | Description |
| --- | --- |
| `bullets` | Bullet list for features, problems, or lessons |
| `bullets+box` | Bullets plus a dark insight box |
| `quote` | Pull quote with optional stat chips |
| `code` | Terminal or prompt block |
| `agents` | Agent tag pills with descriptions |
| `cta` | Command, bullets, and closing question |
| `stats` | Large numeric proof points |

## Brief Rules

- `meta.output` controls the output folder.
- `slides[].id` controls slide order.
- `slides[].bg` must be one of the supported background tokens.
- `slides[].icon` must exist in `icons/library.md`.
- `slides[].content.type` controls the block renderer.
- `slides[].verdict` is rendered as a strong closing line.
- `slides[].swipe: true` adds the swipe prompt.

## Export Rules

1. Generate `output/<meta.output>/slides.html`.
2. Export each `.slide` element to `slide_01.png`, `slide_02.png`, etc.
3. Assemble the PNGs into `<meta.output>.pdf`.
4. Confirm the generated files before reporting completion.

