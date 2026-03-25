"""Parse presentation-level metadata."""

import sqlite3
from pathlib import Path

from pptx import Presentation

from .db import insert_row


def parse_presentation(prs: Presentation, filename: str, conn: sqlite3.Connection, db_no: int) -> int:
    """Insert presentation record and return db_no (the PK)."""
    insert_row(conn, "presentations", {
        "db_no": db_no,
        "filename": Path(filename).name,
        "slide_width": int(prs.slide_width),
        "slide_height": int(prs.slide_height),
    })
    return db_no
