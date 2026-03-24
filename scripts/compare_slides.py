#!/usr/bin/env python3
"""Compare PPTX slides (LibreOffice render) with web viewer (Playwright capture).

Generates side-by-side images: [ PPTX reference | Web viewer ]
saved to ./output/compare/ by default.

Usage:
    # Compare all presentations (frontend=5173, backend=8000)
    python scripts/compare_slides.py

    # Compare a specific presentation by db_no
    python scripts/compare_slides.py --db-no 27

    # Custom ports and output directory
    python scripts/compare_slides.py --fe-port 5173 --be-port 8000 -o /tmp/compare
"""

import argparse
import json
import subprocess
import sys
import tempfile
import urllib.request
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont
from playwright.sync_api import sync_playwright


def fetch_json(url: str):
    with urllib.request.urlopen(url) as resp:
        return json.loads(resp.read())


def render_pptx_to_images(pptx_path: str, out_dir: Path) -> list[Path]:
    """Render PPTX slides to PNG images using LibreOffice."""
    out_dir.mkdir(parents=True, exist_ok=True)
    stem = Path(pptx_path).stem

    # First convert to PDF (handles multi-slide)
    subprocess.run(
        ["libreoffice", "--headless", "--convert-to", "pdf", "--outdir", str(out_dir), pptx_path],
        capture_output=True, timeout=60,
    )
    pdf_path = out_dir / f"{stem}.pdf"
    if not pdf_path.exists():
        return []

    # Convert each PDF page to PNG
    subprocess.run(
        ["pdftoppm", "-png", "-r", "192", str(pdf_path), str(out_dir / "slide")],
        capture_output=True, timeout=60,
    )
    pdf_path.unlink(missing_ok=True)

    # Collect generated slide-N.png files, sorted
    images = sorted(out_dir.glob("slide-*.png"), key=lambda p: int(p.stem.split("-")[1]))
    return images


def capture_web_slides(
    page, pres_id: int, slide_count: int, fe_url: str, out_dir: Path
) -> list[Path]:
    """Capture each slide from the web viewer using Playwright."""
    out_dir.mkdir(parents=True, exist_ok=True)
    images = []

    # Navigate to presentation list, click the target presentation
    page.goto(fe_url)
    page.wait_for_load_state("networkidle")

    # Click the presentation card
    cards = page.locator("[style*='cursor: pointer'], [style*='cursor:pointer']").all()
    clicked = False
    for card in cards:
        text = card.inner_text()
        if f"slides" in text or f"slide" in text:
            # Just click by pres_id order - find the right one
            pass
    # More reliable: use the API to get the slide IDs and navigate
    # Actually, let's click on presentations by index
    page.goto(fe_url)
    page.wait_for_load_state("networkidle")

    # Find all presentation items and click the one we want
    items = page.locator("div[style*='cursor']").all()
    for item in items:
        strong = item.locator("strong")
        if strong.count() > 0:
            # This is a presentation card
            pass

    # Simpler approach: just click on the presentation using its text
    # First get the filename from API
    page.goto(fe_url)
    page.wait_for_load_state("networkidle")

    for slide_idx in range(slide_count):
        # Click on the presentation (re-navigate each time for reliability)
        if slide_idx == 0:
            # Click the presentation from the list
            page.get_by_text(f"{slide_count} slide").nth(0)  # just wait
            # Use a more targeted approach - click the card with the pres info
            all_strongs = page.locator("strong").all()
            for s in all_strongs:
                parent = s.locator("..")
                try:
                    parent.click(timeout=2000)
                    page.wait_for_load_state("networkidle")
                    # Check if we navigated to the slide view
                    if page.locator("button:has-text('Back')").count() > 0:
                        break
                except Exception:
                    continue

        # If multi-slide, navigate to the right slide
        if slide_idx > 0:
            next_btn = page.locator("button:has-text('Next')")
            if next_btn.count() > 0 and next_btn.is_enabled():
                next_btn.click()
                page.wait_for_load_state("networkidle")

        page.wait_for_timeout(300)

        # Take screenshot of the slide canvas area
        out_path = out_dir / f"slide-{slide_idx + 1}.png"
        page.screenshot(path=str(out_path))
        images.append(out_path)

    # Go back to list
    back_btn = page.locator("button:has-text('Back')")
    if back_btn.count() > 0:
        back_btn.click()
        page.wait_for_load_state("networkidle")

    return images


def wait_for_slide_content(page, timeout_ms: int = 5000):
    """Wait for all images and charts to fully render on the current slide."""
    page.wait_for_load_state("networkidle")
    page.locator("text=Loading").wait_for(state="hidden", timeout=timeout_ms)

    # Single evaluate call: wait for all <img> loads and <canvas> readiness
    page.evaluate("""(timeoutMs) => {
        const imgsDone = Promise.all(
            Array.from(document.querySelectorAll('img')).map(img => {
                if (img.complete && img.naturalWidth > 0) return Promise.resolve();
                return new Promise(resolve => {
                    img.addEventListener('load', resolve, { once: true });
                    img.addEventListener('error', resolve, { once: true });
                    setTimeout(resolve, timeoutMs);
                });
            })
        );

        const canvasDone = new Promise(resolve => {
            const check = () => {
                const canvases = document.querySelectorAll('canvas');
                const allReady = Array.from(canvases).every(
                    c => c.width > 0 && c.height > 0
                );
                if (canvases.length === 0 || allReady) resolve();
                else setTimeout(check, 100);
            };
            check();
            setTimeout(resolve, timeoutMs);
        });

        return Promise.all([imgsDone, canvasDone]);
    }""", timeout_ms)

    # Allow final paint
    page.wait_for_timeout(300)


def capture_web_slides_v2(
    page, pres: dict, be_url: str, fe_url: str, out_dir: Path
) -> list[Path]:
    """Capture slides by navigating directly via clicking the correct presentation."""
    out_dir.mkdir(parents=True, exist_ok=True)
    images = []
    filename = pres["filename"]
    slide_count = pres["slide_count"]

    page.goto(fe_url)
    page.wait_for_load_state("networkidle")

    # Click on the presentation by filename
    page.get_by_text(filename).first.click()
    wait_for_slide_content(page)

    slide_area = page.locator("div[style*='box-shadow']")

    for slide_idx in range(slide_count):
        if slide_idx > 0:
            next_btn = page.get_by_role("button", name="Next →")
            if next_btn.is_enabled():
                next_btn.click()
                wait_for_slide_content(page)

        out_path = out_dir / f"slide-{slide_idx + 1}.png"
        if slide_area.count() > 0 and slide_area.first.is_visible():
            slide_area.first.screenshot(path=str(out_path))
        else:
            page.screenshot(path=str(out_path))
        images.append(out_path)

    # Go back
    page.get_by_role("button", name="← Back").click()
    page.wait_for_load_state("networkidle")

    return images


def add_label(img: Image.Image, label: str, bg_color: str = "#222") -> Image.Image:
    """Add a label bar on top of an image."""
    bar_h = 36
    new = Image.new("RGB", (img.width, img.height + bar_h), bg_color)
    draw = ImageDraw.Draw(new)
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 18)
    except OSError:
        font = ImageFont.load_default()
    bbox = draw.textbbox((0, 0), label, font=font)
    tw = bbox[2] - bbox[0]
    draw.text(((img.width - tw) // 2, (bar_h - 18) // 2), label, fill="white", font=font)
    new.paste(img, (0, bar_h))
    return new


def concat_side_by_side(
    ref_path: Path, web_path: Path, out_path: Path, pres_name: str, slide_num: int
):
    """Concatenate reference and web images side by side with labels."""
    ref_img = Image.open(ref_path).convert("RGB")
    web_img = Image.open(web_path).convert("RGB")

    # Normalize heights to match
    target_h = max(ref_img.height, web_img.height)
    if ref_img.height != target_h:
        ratio = target_h / ref_img.height
        ref_img = ref_img.resize((int(ref_img.width * ratio), target_h), Image.LANCZOS)
    if web_img.height != target_h:
        ratio = target_h / web_img.height
        web_img = web_img.resize((int(web_img.width * ratio), target_h), Image.LANCZOS)

    # Add labels
    ref_labeled = add_label(ref_img, f"PPTX (LibreOffice) - {pres_name} Slide {slide_num}")
    web_labeled = add_label(web_img, f"Web Viewer - {pres_name} Slide {slide_num}")

    # Add a 4px separator
    sep = 4
    total_w = ref_labeled.width + sep + web_labeled.width
    total_h = ref_labeled.height
    canvas = Image.new("RGB", (total_w, total_h), "#444")
    canvas.paste(ref_labeled, (0, 0))
    canvas.paste(web_labeled, (ref_labeled.width + sep, 0))

    out_path.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(str(out_path), quality=92)


def find_pptx_path(samples_dir: Path, db_no: int) -> Path | None:
    """Find the PPTX file for a given db_no in the samples directory."""
    sample_dir = samples_dir / str(db_no)
    if not sample_dir.is_dir():
        return None
    pptx_files = list(sample_dir.glob("*.pptx"))
    return pptx_files[0] if pptx_files else None


def main():
    parser = argparse.ArgumentParser(description="Compare PPTX slides with web viewer")
    parser.add_argument("--db-no", type=int, default=None, help="Compare only this db_no")
    parser.add_argument("--fe-port", type=int, default=5173, help="Frontend port (default: 5173)")
    parser.add_argument("--be-port", type=int, default=8000, help="Backend port (default: 8000)")
    parser.add_argument("-o", "--output", default="output/compare", help="Output directory")
    parser.add_argument("--samples-dir", default="samples", help="Samples directory")
    args = parser.parse_args()

    fe_url = f"http://localhost:{args.fe_port}"
    be_url = f"http://localhost:{args.be_port}"
    out_root = Path(args.output)
    samples_dir = Path(args.samples_dir)

    # Fetch presentation list from API
    try:
        presentations = fetch_json(f"{be_url}/api/presentations")
    except Exception as e:
        print(f"Cannot reach backend at {be_url}: {e}", file=sys.stderr)
        sys.exit(1)

    if args.db_no is not None:
        presentations = [p for p in presentations if p["db_no"] == args.db_no]
        if not presentations:
            print(f"No presentation with db_no={args.db_no}", file=sys.stderr)
            sys.exit(1)

    print(f"Comparing {len(presentations)} presentation(s)...")
    print(f"Output: {out_root.resolve()}\n")

    with sync_playwright() as pw:
        browser = pw.chromium.launch()
        page = browser.new_page(viewport={"width": 1400, "height": 900})

        for pres in presentations:
            db_no = pres["db_no"]
            filename = pres["filename"]
            stem = Path(filename).stem
            slide_count = pres["slide_count"]

            print(f"[{db_no:>3}] {filename} ({slide_count} slide(s))")

            # 1) Render PPTX via LibreOffice
            pptx_path = find_pptx_path(samples_dir, db_no)
            if pptx_path is None:
                print(f"  SKIP - PPTX not found in {samples_dir}/{db_no}/")
                continue

            with tempfile.TemporaryDirectory() as tmp:
                tmp_path = Path(tmp)
                ref_images = render_pptx_to_images(str(pptx_path), tmp_path / "ref")

                if len(ref_images) == 0:
                    print("  SKIP - LibreOffice render failed")
                    continue

                # 2) Capture web viewer
                web_images = capture_web_slides_v2(page, pres, be_url, fe_url, tmp_path / "web")

                # 3) Concat side by side
                n = min(len(ref_images), len(web_images))
                for i in range(n):
                    out_name = f"{db_no:03d}_{stem}_slide{i + 1}.png"
                    out_path = out_root / out_name
                    concat_side_by_side(ref_images[i], web_images[i], out_path, filename, i + 1)
                    print(f"  -> {out_path}")

        browser.close()

    print(f"\nDone! {out_root.resolve()}")


if __name__ == "__main__":
    main()
