"""Slide endpoints."""

from fastapi import APIRouter, HTTPException
from fastapi.responses import Response

from ..database import get_db
from ..services.slide_service import get_slide_data

router = APIRouter(prefix="/api/slides", tags=["slides"])


@router.get("/{slide_id}")
def get_slide(slide_id: int):
    with get_db() as conn:
        data = get_slide_data(slide_id, conn)
        if not data:
            raise HTTPException(404, "Slide not found")
        return data


@router.get("/{slide_id}/image")
def get_slide_image(slide_id: int):
    with get_db() as conn:
        row = conn.execute(
            "SELECT data, content_type, width, height FROM slide_images WHERE slide_id = ?",
            (slide_id,),
        ).fetchone()
        if not row:
            raise HTTPException(404, "Slide image not found")
        return Response(
            content=row["data"],
            media_type=row["content_type"],
            headers={"Cache-Control": "public, max-age=86400"},
        )
