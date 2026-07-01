from __future__ import annotations

import argparse
import asyncio
from pathlib import Path

import img2pdf
from PIL import Image, JpegImagePlugin
from playwright.async_api import async_playwright


_ = JpegImagePlugin


async def export_slides(slides_html: Path, only_slide: int | None = None) -> list[Path]:
    slides_html = slides_html.resolve()
    output_dir = slides_html.parent
    exported: list[Path] = []

    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch()
        page = await browser.new_page(viewport={"width": 1080, "height": 1080}, device_scale_factor=2)
        await page.goto(slides_html.as_uri(), wait_until="networkidle")
        await page.locator(".slide").first.wait_for()
        count = await page.locator(".slide").count()

        indices = [only_slide - 1] if only_slide else list(range(count))
        for index in indices:
            if index < 0 or index >= count:
                raise ValueError(f"Slide {index + 1} does not exist. Deck has {count} slides.")
            path = output_dir / f"slide_{index + 1:02}.png"
            await page.locator(".slide").nth(index).screenshot(path=str(path))
            exported.append(path)

        await browser.close()

    return exported


def assemble_pdf(image_paths: list[Path], pdf_path: Path) -> None:
    if not image_paths:
        return
    pdf_path.write_bytes(img2pdf.convert([str(p) for p in image_paths]))


def existing_slide_paths(output_dir: Path) -> list[Path]:
    return sorted(output_dir.glob("slide_*.png"))


async def main_async() -> None:
    parser = argparse.ArgumentParser(description="Export Slide Hustle slides to PNG and PDF.")
    parser.add_argument("slides_html", type=Path, help="Path to generated slides.html.")
    parser.add_argument("--slide", type=int, help="Only export one slide number.")
    parser.add_argument("--no-pdf", action="store_true", help="Skip PDF assembly.")
    parser.add_argument(
        "--rebuild-pdf",
        action="store_true",
        help="After a single-slide export, reassemble the PDF from all existing slide PNGs.",
    )
    args = parser.parse_args()

    exported = await export_slides(args.slides_html, args.slide)
    output_dir = args.slides_html.resolve().parent
    pdf_path = output_dir / f"{output_dir.name}.pdf"

    if args.rebuild_pdf:
        assemble_pdf(existing_slide_paths(output_dir), pdf_path)
        print(f"Rebuilt {pdf_path}")
    elif not args.no_pdf and args.slide is None:
        assemble_pdf(existing_slide_paths(output_dir), pdf_path)
        print(f"Exported {pdf_path}")

    for path in exported:
        print(f"Exported {path}")


def main() -> None:
    asyncio.run(main_async())


if __name__ == "__main__":
    main()
