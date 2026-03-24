"""Slide endpoints."""

from fastapi import APIRouter, HTTPException

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
