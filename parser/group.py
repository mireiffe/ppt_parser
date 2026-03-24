"""Parse group shapes recursively."""

import sqlite3

from .image import ImageStore
from .shape import parse_shape


def parse_group_children(group_shape, group_shape_id: int, conn: sqlite3.Connection,
                         image_store: ImageStore, theme_colors: dict | None = None,
                         slide_id: int | None = None,
                         slide_master_id: int | None = None,
                         slide_layout_id: int | None = None):
    """Recursively parse all children of a group shape."""
    for z_idx, child in enumerate(group_shape.shapes):
        parse_shape(
            child, conn, image_store, theme_colors,
            slide_id=slide_id,
            slide_master_id=slide_master_id,
            slide_layout_id=slide_layout_id,
            z_order=z_idx,
            parent_group_id=group_shape_id,
        )
