"""Capture slide images using LibreOffice headless + pypdfium2."""

import io
import sqlite3
import subprocess
import tempfile
from pathlib import Path

import pypdfium2 as pdfium
from PIL import Image

from .db import insert_row


def capture_slides(pptx_path: str | Path, conn: sqlite3.Connection, scale: float = 2.0) -> int:
    """
    Render each slide of a PPTX as a high-quality PNG and store in slide_images table.

    Steps:
      1. Convert PPTX → PDF via LibreOffice headless
      2. Render each PDF page as PNG via pypdfium2
      3. Match page index to slide_number and insert into slide_images

    Returns the number of images captured.
    """
    pptx_path = Path(pptx_path)

    with tempfile.TemporaryDirectory() as tmpdir:
        # 1. PPTX → PDF
        subprocess.run(
            [
                "libreoffice", "--headless", "--convert-to", "pdf",
                "--outdir", tmpdir, str(pptx_path),
            ],
            check=True,
            capture_output=True,
            timeout=120,
        )

        pdf_path = Path(tmpdir) / pptx_path.with_suffix(".pdf").name
        if not pdf_path.exists():
            raise FileNotFoundError(f"LibreOffice failed to produce PDF: {pdf_path}")

        # 2. Render each page
        pdf = pdfium.PdfDocument(str(pdf_path))
        count = 0

        # Get slide_id mapping: slide_number → slide_id
        # We need the presentation's db_no to scope correctly.
        # Use the filename matched to the most recently inserted presentation.
        filename = pptx_path.name
        row = conn.execute(
            "SELECT db_no FROM presentations WHERE filename = ? ORDER BY created_at DESC LIMIT 1",
            (filename,),
        ).fetchone()
        if not row:
            raise ValueError(f"No presentation found for filename: {filename}")

        db_no = row[0]
        slide_rows = conn.execute(
            "SELECT id, slide_number FROM slides WHERE presentation_id = ? ORDER BY slide_number",
            (db_no,),
        ).fetchall()
        slide_map = {r[1]: r[0] for r in slide_rows}  # slide_number → slide_id

        for page_idx in range(len(pdf)):
            slide_number = page_idx + 1
            slide_id = slide_map.get(slide_number)
            if slide_id is None:
                continue

            page = pdf[page_idx]
            bitmap = page.render(scale=scale)
            pil_image = bitmap.to_pil()

            buf = io.BytesIO()
            pil_image.save(buf, format="PNG", optimize=True)
            png_data = buf.getvalue()

            insert_row(conn, "slide_images", {
                "slide_id": slide_id,
                "content_type": "image/png",
                "width": pil_image.width,
                "height": pil_image.height,
                "data": png_data,
            })
            count += 1

        pdf.close()

    return count
