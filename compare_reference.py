from __future__ import annotations

import argparse
import hashlib
import shutil
import subprocess
import tempfile
from pathlib import Path

from PIL import Image, ImageChops, ImageStat


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def render_pdf_with_pymupdf(pdf_path: Path, output_dir: Path) -> list[Path]:
    try:
        import fitz
    except ImportError as exc:
        raise RuntimeError("PyMuPDF is not installed.") from exc

    rendered: list[Path] = []
    document = fitz.open(pdf_path)
    try:
        for index, page in enumerate(document, start=1):
            scale = 1080 / page.rect.width
            pixmap = page.get_pixmap(matrix=fitz.Matrix(scale, scale), alpha=False)
            path = output_dir / f"reference-{index:02}.png"
            pixmap.save(path)
            rendered.append(path)
    finally:
        document.close()
    return rendered


def render_pdf_with_poppler(pdf_path: Path, output_dir: Path) -> list[Path]:
    pdftoppm = shutil.which("pdftoppm")
    if not pdftoppm:
        raise RuntimeError(
            "Neither PyMuPDF nor pdftoppm is available. Install dependencies with "
            "`pip install -r requirements.txt`, or install Poppler (macOS: brew install poppler)."
        )

    prefix = output_dir / "reference"
    subprocess.run(
        [pdftoppm, "-png", "-r", "72", str(pdf_path), str(prefix)],
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    return sorted(output_dir.glob("reference-*.png"))


def render_pdf(pdf_path: Path, output_dir: Path) -> list[Path]:
    try:
        return render_pdf_with_pymupdf(pdf_path, output_dir)
    except RuntimeError:
        return render_pdf_with_poppler(pdf_path, output_dir)


def compare_images(
    reference: Path, generated: Path, resize_reference: bool
) -> tuple[bool, float, tuple[int, int] | None]:
    with Image.open(reference) as ref_image, Image.open(generated) as gen_image:
        ref = ref_image.convert("RGB")
        gen = gen_image.convert("RGB")
        if ref.size != gen.size:
            if not resize_reference:
                return False, 100.0, None
            ref = ref.resize(gen.size, Image.Resampling.LANCZOS)

        diff = ImageChops.difference(ref, gen)
        bbox = diff.getbbox()
        if bbox is None:
            return True, 0.0, ref.size

        stat = ImageStat.Stat(diff)
        mean_delta = sum(stat.mean) / len(stat.mean)
        normalized = (mean_delta / 255) * 100
        return False, normalized, ref.size


def existing_slide_paths(output_dir: Path) -> list[Path]:
    return sorted(output_dir.glob("slide_*.png"))


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Compare generated Slide Hustle PNG slides against a reference PDF or PNG folder."
    )
    parser.add_argument("reference", type=Path, help="Reference PDF file or folder of slide_*.png files.")
    parser.add_argument("generated", type=Path, help="Generated output folder containing slide_*.png files.")
    parser.add_argument("--tolerance", type=float, default=15.0, help="Allowed mean pixel delta percent.")
    parser.add_argument(
        "--no-resize-reference",
        action="store_true",
        help="Fail on size mismatch instead of resizing reference pages to generated slide dimensions.",
    )
    args = parser.parse_args()

    generated = existing_slide_paths(args.generated)
    if not generated:
        raise SystemExit(f"No generated slide_*.png files found in {args.generated}")

    with tempfile.TemporaryDirectory() as tmp:
        tmp_dir = Path(tmp)
        if args.reference.is_file() and args.reference.suffix.lower() == ".pdf":
            references = render_pdf(args.reference, tmp_dir)
        elif args.reference.is_dir():
            references = existing_slide_paths(args.reference)
        else:
            raise SystemExit("Reference must be a PDF file or a folder containing slide_*.png files.")

        if len(references) != len(generated):
            raise SystemExit(f"Slide count mismatch: reference={len(references)} generated={len(generated)}")

        failures = 0
        for index, (reference, generated_slide) in enumerate(zip(references, generated), start=1):
            exact_hash = sha256(reference) == sha256(generated_slide)
            identical, delta, size = compare_images(
                reference, generated_slide, resize_reference=not args.no_resize_reference
            )
            passed = identical or delta <= args.tolerance
            failures += 0 if passed else 1
            size_label = f"{size[0]}x{size[1]}" if size else "size-mismatch"
            print(
                f"slide_{index:02}: passed={passed} exact_hash={exact_hash} "
                f"mean_delta={delta:.4f}% size={size_label}"
            )

        if failures:
            raise SystemExit(f"{failures} slide comparison(s) failed.")

        print("All slides match within tolerance.")


if __name__ == "__main__":
    main()
