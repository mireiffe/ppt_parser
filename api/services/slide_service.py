"""Assemble full slide render data with inheritance resolution."""

import json
import sqlite3


def _resolve_background(slide_row, conn: sqlite3.Connection) -> dict:
    """Resolve background: slide → layout → master inheritance chain."""
    # Check slide's own background
    if slide_row["bg_fill_type"]:
        return {
            "fill_type": slide_row["bg_fill_type"],
            "fill_color": slide_row["bg_fill_color"],
            "fill_json": json.loads(slide_row["bg_fill_json"]) if slide_row["bg_fill_json"] else None,
        }

    # Check layout
    if slide_row["slide_layout_id"]:
        layout = conn.execute(
            "SELECT * FROM slide_layouts WHERE id = ?", (slide_row["slide_layout_id"],)
        ).fetchone()
        if layout and layout["bg_fill_type"]:
            return {
                "fill_type": layout["bg_fill_type"],
                "fill_color": layout["bg_fill_color"],
                "fill_json": json.loads(layout["bg_fill_json"]) if layout["bg_fill_json"] else None,
            }

        # Check master
        if layout and layout["slide_master_id"]:
            master = conn.execute(
                "SELECT * FROM slide_masters WHERE id = ?", (layout["slide_master_id"],)
            ).fetchone()
            if master and master["bg_fill_type"]:
                return {
                    "fill_type": master["bg_fill_type"],
                    "fill_color": master["bg_fill_color"],
                    "fill_json": json.loads(master["bg_fill_json"]) if master["bg_fill_json"] else None,
                }

    return {"fill_type": "solid", "fill_color": "#FFFFFF", "fill_json": None}


def _build_text_frame(tf_row, conn: sqlite3.Connection) -> dict | None:
    """Build nested text frame data."""
    if tf_row is None:
        return None

    paragraphs = conn.execute(
        "SELECT * FROM paragraphs WHERE text_frame_id = ? ORDER BY paragraph_index",
        (tf_row["id"],)
    ).fetchall()

    para_list = []
    for p in paragraphs:
        runs = conn.execute(
            "SELECT * FROM runs WHERE paragraph_id = ? ORDER BY run_index",
            (p["id"],)
        ).fetchall()

        run_list = []
        for r in runs:
            run_data = {
                "text": r["text"],
                "font_name": r["font_name"],
                "font_size": r["font_size"],
                "font_bold": bool(r["font_bold"]) if r["font_bold"] is not None else None,
                "font_italic": bool(r["font_italic"]) if r["font_italic"] is not None else None,
                "font_underline": r["font_underline"],
                "font_color": r["font_color"],
                "font_color_theme": r["font_color_theme"],
                "is_line_break": bool(r["is_line_break"]),
                "hyperlink_url": r["hyperlink_url"],
            }
            run_list.append(run_data)

        para_data = {
            "alignment": p["alignment"],
            "level": p["level"],
            "space_before": p["space_before"],
            "space_after": p["space_after"],
            "line_spacing": p["line_spacing"],
            "line_spacing_rule": p["line_spacing_rule"],
            "bullet_type": p["bullet_type"],
            "bullet_char": p["bullet_char"],
            "bullet_color": p["bullet_color"],
            "indent": p["indent"],
            "margin_left": p["margin_left"],
            "runs": run_list,
        }
        para_list.append(para_data)

    return {
        "word_wrap": bool(tf_row["word_wrap"]) if tf_row["word_wrap"] is not None else True,
        "auto_size": tf_row["auto_size"],
        "margin_left": tf_row["margin_left"],
        "margin_right": tf_row["margin_right"],
        "margin_top": tf_row["margin_top"],
        "margin_bottom": tf_row["margin_bottom"],
        "vertical_anchor": tf_row["vertical_anchor"],
        "text_direction": tf_row["text_direction"],
        "paragraphs": para_list,
    }


def _build_table_data(shape_id: int, conn: sqlite3.Connection) -> dict | None:
    """Build table data for a table shape."""
    dims = conn.execute(
        "SELECT * FROM table_dimensions WHERE shape_id = ?", (shape_id,)
    ).fetchone()
    if not dims:
        return None

    cells = conn.execute(
        "SELECT * FROM table_cells WHERE shape_id = ? ORDER BY row_idx, col_idx",
        (shape_id,)
    ).fetchall()

    cell_list = []
    for c in cells:
        cell_tf = None
        if c["text_frame_id"]:
            tf_row = conn.execute(
                "SELECT * FROM text_frames WHERE id = ?", (c["text_frame_id"],)
            ).fetchone()
            cell_tf = _build_text_frame(tf_row, conn)

        cell_data = {
            "row_idx": c["row_idx"],
            "col_idx": c["col_idx"],
            "row_span": c["row_span"],
            "col_span": c["col_span"],
            "is_merge_origin": bool(c["is_merge_origin"]),
            "fill_type": c["fill_type"],
            "fill_color": c["fill_color"],
            "vertical_anchor": c["vertical_anchor"],
            "borders": {
                "left": {"color": c["border_left_color"], "width": c["border_left_width"]},
                "right": {"color": c["border_right_color"], "width": c["border_right_width"]},
                "top": {"color": c["border_top_color"], "width": c["border_top_width"]},
                "bottom": {"color": c["border_bottom_color"], "width": c["border_bottom_width"]},
            },
            "text_frame": cell_tf,
        }
        cell_list.append(cell_data)

    return {
        "num_rows": dims["num_rows"],
        "num_cols": dims["num_cols"],
        "col_widths": json.loads(dims["col_widths_json"]),
        "row_heights": json.loads(dims["row_heights_json"]),
        "cells": cell_list,
    }


def _build_shape(shape_row, conn: sqlite3.Connection) -> dict:
    """Build shape data with nested text frame and table."""
    shape = dict(shape_row)
    shape_id = shape["id"]

    # Fill
    fill = None
    if shape["fill_type"]:
        fill = {
            "type": shape["fill_type"],
            "color": shape["fill_color"],
            "opacity": shape["fill_opacity"],
        }
        if shape["fill_json"]:
            fill["details"] = json.loads(shape["fill_json"])

    # Line
    line = None
    if shape["line_color"] or shape["line_width"]:
        line = {
            "color": shape["line_color"],
            "width": shape["line_width"],
            "dash_style": shape["line_dash_style"],
        }

    # Shadow
    shadow = json.loads(shape["shadow_json"]) if shape["shadow_json"] else None

    # Text frame
    text_frame = None
    tf_row = conn.execute(
        "SELECT * FROM text_frames WHERE shape_id = ?", (shape_id,)
    ).fetchone()
    if tf_row:
        text_frame = _build_text_frame(tf_row, conn)

    # Table
    table = None
    if shape["shape_type"] == "table":
        table = _build_table_data(shape_id, conn)

    # Children (for groups)
    children = None
    if shape["shape_type"] == "group":
        child_rows = conn.execute(
            "SELECT * FROM shapes WHERE parent_group_id = ? ORDER BY z_order",
            (shape_id,)
        ).fetchall()
        children = [_build_shape(c, conn) for c in child_rows]

    result = {
        "id": shape_id,
        "shape_type": shape["shape_type"],
        "name": shape["name"],
        "preset_geometry": shape["preset_geometry"],
        "pos_x": shape["pos_x"],
        "pos_y": shape["pos_y"],
        "width": shape["width"],
        "height": shape["height"],
        "rotation": shape["rotation"],
        "flip_h": bool(shape["flip_h"]),
        "flip_v": bool(shape["flip_v"]),
        "z_order": shape["z_order"],
        "placeholder_type": shape["placeholder_type"],
        "fill": fill,
        "line": line,
        "shadow": shadow,
        "text_frame": text_frame,
        "table": table,
        "children": children,
        "hyperlink_url": shape["hyperlink_url"],
    }

    # Picture-specific
    if shape["shape_type"] == "picture" and shape["media_id"]:
        result["media_url"] = f"/api/media/{shape['media_id']}"
        result["crop"] = {
            "left": shape["crop_left"],
            "top": shape["crop_top"],
            "right": shape["crop_right"],
            "bottom": shape["crop_bottom"],
        }

    # Connector-specific
    if shape["shape_type"] == "connector":
        result["begin_x"] = shape["begin_x"]
        result["begin_y"] = shape["begin_y"]
        result["end_x"] = shape["end_x"]
        result["end_y"] = shape["end_y"]

    # Group-specific
    if shape["shape_type"] == "group":
        result["group_transform"] = {
            "ch_off_x": shape["group_ch_off_x"],
            "ch_off_y": shape["group_ch_off_y"],
            "ch_ext_cx": shape["group_ch_ext_cx"],
            "ch_ext_cy": shape["group_ch_ext_cy"],
        }

    return result


def get_slide_data(slide_id: int, conn: sqlite3.Connection) -> dict | None:
    """Get complete slide render data."""
    slide = conn.execute("SELECT * FROM slides WHERE id = ?", (slide_id,)).fetchone()
    if not slide:
        return None

    background = _resolve_background(slide, conn)

    # Get notes
    notes_row = conn.execute(
        "SELECT text FROM slide_notes WHERE slide_id = ?", (slide_id,)
    ).fetchone()
    notes = notes_row["text"] if notes_row else None

    # Get top-level shapes (no parent group)
    shapes = conn.execute(
        "SELECT * FROM shapes WHERE slide_id = ? AND parent_group_id IS NULL ORDER BY z_order",
        (slide_id,)
    ).fetchall()

    shape_list = [_build_shape(s, conn) for s in shapes]

    # Get presentation dimensions
    pres = conn.execute(
        "SELECT slide_width, slide_height FROM presentations WHERE id = ?",
        (slide["presentation_id"],)
    ).fetchone()

    return {
        "id": slide_id,
        "slide_number": slide["slide_number"],
        "slide_width": pres["slide_width"] if pres else None,
        "slide_height": pres["slide_height"] if pres else None,
        "background": background,
        "notes": notes,
        "shapes": shape_list,
    }
