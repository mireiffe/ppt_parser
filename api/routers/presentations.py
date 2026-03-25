"""Presentation endpoints."""

import tempfile
from pathlib import Path

from fastapi import APIRouter, HTTPException, UploadFile, File, Form

from ..database import get_db

router = APIRouter(prefix="/api/presentations", tags=["presentations"])


@router.get("")
def list_presentations():
    with get_db() as conn:
        rows = conn.execute("""
            SELECT p.db_no, p.filename, p.slide_width, p.slide_height,
                   (SELECT COUNT(*) FROM slides s WHERE s.presentation_id = p.db_no) as slide_count
            FROM presentations p
            ORDER BY p.db_no
        """).fetchall()
        return [dict(r) for r in rows]


@router.get("/{db_no}")
def get_presentation(db_no: int):
    with get_db() as conn:
        pres = conn.execute(
            "SELECT * FROM presentations WHERE db_no = ?", (db_no,)
        ).fetchone()
        if not pres:
            raise HTTPException(404, "Presentation not found")

        theme = conn.execute(
            "SELECT * FROM themes WHERE presentation_id = ?", (db_no,)
        ).fetchone()

        slides = conn.execute(
            "SELECT id, slide_number, name FROM slides WHERE presentation_id = ? ORDER BY slide_number",
            (db_no,)
        ).fetchall()

        return {
            **dict(pres),
            "theme": dict(theme) if theme else None,
            "slides": [dict(s) for s in slides],
        }


@router.post("/upload")
async def upload_presentation(file: UploadFile = File(...), db_no: int = Form(...)):
    if not file.filename or not file.filename.endswith(".pptx"):
        raise HTTPException(400, "Only .pptx files are accepted")

    with tempfile.NamedTemporaryFile(suffix=".pptx", delete=False) as tmp:
        content = await file.read()
        tmp.write(content)
        tmp_path = tmp.name

    try:
        from parser.cli import parse_pptx
        from ..database import _db_path
        parse_pptx(tmp_path, _db_path, db_no=db_no)
        return {"message": f"Parsed {file.filename} successfully"}
    except Exception as e:
        raise HTTPException(500, f"Parse error: {e}")
    finally:
        Path(tmp_path).unlink(missing_ok=True)
