"""Media (image) serving endpoint."""

from fastapi import APIRouter, HTTPException
from fastapi.responses import Response

from ..database import get_db

router = APIRouter(prefix="/api/media", tags=["media"])


@router.get("/{media_id}")
def get_media(media_id: int):
    with get_db() as conn:
        row = conn.execute(
            "SELECT data, content_type, filename FROM media WHERE id = ?",
            (media_id,)
        ).fetchone()
        if not row:
            raise HTTPException(404, "Media not found")
        return Response(
            content=row["data"],
            media_type=row["content_type"] or "application/octet-stream",
            headers={"Content-Disposition": f'inline; filename="{row["filename"] or "image"}"'},
        )
