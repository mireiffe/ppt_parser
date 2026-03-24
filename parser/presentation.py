"""Parse presentation-level metadata."""

import sqlite3
from pathlib import Path

from pptx import Presentation

from .db import insert_row


def parse_presentation(prs: Presentation, filename: str, conn: sqlite3.Connection) -> int:
    """Insert presentation record and return its id."""
    return insert_row(conn, "presentations", {
        "filename": Path(filename).name,
        "slide_width": int(prs.slide_width),
        "slide_height": int(prs.slide_height),
    })
