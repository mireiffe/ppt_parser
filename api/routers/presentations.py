"""Presentation endpoints."""

import tempfile
from pathlib import Path

from fastapi import APIRouter, HTTPException, UploadFile, File

from ..database import get_db

router = APIRouter(prefix="/api/presentations", tags=["presentations"])


@router.get("")
def list_presentations():
    with get_db() as conn:
        rows = conn.execute("""
            SELECT p.id, p.filename, p.slide_width, p.slide_height,
                   (SELECT COUNT(*) FROM slides s WHERE s.presentation_id = p.id) as slide_count
            FROM presentations p
            ORDER BY p.id
        """).fetchall()
        return [dict(r) for r in rows]


@router.get("/{pres_id}")
def get_presentation(pres_id: int):
    with get_db() as conn:
        pres = conn.execute(
            "SELECT * FROM presentations WHERE id = ?", (pres_id,)
        ).fetchone()
        if not pres:
            raise HTTPException(404, "Presentation not found")

        theme = conn.execute(
            "SELECT * FROM themes WHERE presentation_id = ?", (pres_id,)
        ).fetchone()

        slides = conn.execute(
            "SELECT id, slide_number, name FROM slides WHERE presentation_id = ? ORDER BY slide_number",
            (pres_id,)
        ).fetchall()

        return {
            **dict(pres),
            "theme": dict(theme) if theme else None,
            "slides": [dict(s) for s in slides],
        }


@router.post("/upload")
async def upload_presentation(file: UploadFile = File(...)):
    if not file.filename or not file.filename.endswith(".pptx"):
        raise HTTPException(400, "Only .pptx files are accepted")

    with tempfile.NamedTemporaryFile(suffix=".pptx", delete=False) as tmp:
        content = await file.read()
        tmp.write(content)
        tmp_path = tmp.name

    try:
        from parser.cli import parse_pptx
        from ..database import _db_path
        parse_pptx(tmp_path, _db_path)
        return {"message": f"Parsed {file.filename} successfully"}
    except Exception as e:
        raise HTTPException(500, f"Parse error: {e}")
    finally:
        Path(tmp_path).unlink(missing_ok=True)
