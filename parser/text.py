"""Parse text frames, paragraphs, and runs."""

import sqlite3

from pptx.util import Emu, Pt

from .color import resolve_color
from .db import insert_row
from .xml_util import get_text_direction


def _emu_or_none(val) -> int | None:
    """Convert a Length/Emu value to int, or None."""
    if val is None:
        return None
    return int(val)


def _font_size_centipoints(font) -> int | None:
    """Get font size in centi-points (1800 = 18pt). None if inherited."""
    size = font.size
    if size is None:
        return None
    # font.size is a Length in EMU; convert to centi-points
    # 1 pt = 12700 EMU, centi-points = size_emu / 12700 * 100 = size_emu / 127
    return round(int(size) / 127)


def _line_spacing_value(para) -> tuple[float | None, str | None]:
    """Extract line spacing as (value, rule)."""
    ls = para.line_spacing
    if ls is None:
        return None, None
    if isinstance(ls, (int, float)):
        return float(ls), "MULTIPLE"
    # It's a Length object (exact spacing)
    return float(int(ls) / 127) / 100, "EXACT"  # convert EMU to points


def _spacing_emu(val) -> int | None:
    """Convert spacing value to EMU."""
    if val is None:
        return None
    return int(val)


def parse_text_frame(shape, shape_id: int, conn: sqlite3.Connection,
                     theme_colors: dict | None = None) -> int | None:
    """Parse a shape's text frame into text_frames/paragraphs/runs tables.
    Returns text_frame_id or None if no text frame.
    """
    if not shape.has_text_frame:
        return None

    tf = shape.text_frame

    # Text direction from XML (not exposed in python-pptx API)
    text_dir = get_text_direction(shape)

    tf_id = insert_row(conn, "text_frames", {
        "shape_id": shape_id,
        "word_wrap": tf.word_wrap if tf.word_wrap is not None else True,
        "auto_size": tf.auto_size.name if tf.auto_size else None,
        "margin_left": _emu_or_none(tf.margin_left),
        "margin_right": _emu_or_none(tf.margin_right),
        "margin_top": _emu_or_none(tf.margin_top),
        "margin_bottom": _emu_or_none(tf.margin_bottom),
        "vertical_anchor": tf.vertical_anchor.name if tf.vertical_anchor else None,
        "text_direction": text_dir,
    })

    for p_idx, para in enumerate(tf.paragraphs):
        _parse_paragraph(para, p_idx, tf_id, conn, theme_colors)

    return tf_id


def _parse_paragraph(para, p_idx: int, tf_id: int, conn: sqlite3.Connection,
                     theme_colors: dict | None = None):
    """Parse a single paragraph."""
    ls_val, ls_rule = _line_spacing_value(para)

    # Bullet properties
    bullet_type = None
    bullet_char = None
    bullet_color = None
    bullet_size_pct = None

    pf = para._pPr  # paragraph properties XML element
    if pf is not None:
        from .xml_util import xpath
        bu_none = xpath(pf, "a:buNone")
        bu_char = xpath(pf, "a:buChar")
        bu_auto = xpath(pf, "a:buAutoNum")
        if bu_none:
            bullet_type = "NONE"
        elif bu_char:
            bullet_type = "CHAR"
            bullet_char = bu_char[0].get("char")
        elif bu_auto:
            bullet_type = "AUTO_NUMBER"

        bu_clr = xpath(pf, "a:buClr/a:srgbClr")
        if bu_clr:
            val = bu_clr[0].get("val", "")
            if len(val) == 6:
                bullet_color = f"#{val.upper()}"

        bu_sz_pct = xpath(pf, "a:buSzPct")
        if bu_sz_pct:
            raw = bu_sz_pct[0].get("val", "")
            if raw:
                bullet_size_pct = int(raw) / 1000  # stored as thousandths of percent

    para_id = insert_row(conn, "paragraphs", {
        "text_frame_id": tf_id,
        "paragraph_index": p_idx,
        "alignment": para.alignment.name if para.alignment else None,
        "level": para.level if para.level else 0,
        "space_before": _spacing_emu(para.space_before),
        "space_after": _spacing_emu(para.space_after),
        "line_spacing": ls_val,
        "line_spacing_rule": ls_rule,
        "bullet_type": bullet_type,
        "bullet_char": bullet_char,
        "bullet_color": bullet_color,
        "bullet_size_pct": bullet_size_pct,
        "indent": _emu_or_none(para.indent) if hasattr(para, "indent") else None,
        "margin_left": _emu_or_none(para.margin_left) if hasattr(para, "margin_left") else None,
    })

    for r_idx, run in enumerate(para.runs):
        _parse_run(run, r_idx, para_id, conn, theme_colors)

    # Handle line breaks within paragraph (they appear as <a:br/> between runs)
    # python-pptx includes them in runs, but if paragraph has no runs and just text,
    # we still need at least one run entry
    if not para.runs and para.text:
        insert_row(conn, "runs", {
            "paragraph_id": para_id,
            "run_index": 0,
            "text": para.text,
        })


def _parse_run(run, r_idx: int, para_id: int, conn: sqlite3.Connection,
               theme_colors: dict | None = None):
    """Parse a single text run."""
    font = run.font
    font_color, font_color_theme, brightness = resolve_color(
        font.color, theme_colors
    )

    insert_row(conn, "runs", {
        "paragraph_id": para_id,
        "run_index": r_idx,
        "text": run.text,
        "font_name": font.name,
        "font_size": _font_size_centipoints(font),
        "font_bold": font.bold,
        "font_italic": font.italic,
        "font_underline": font.underline.name if font.underline and font.underline is not True else (
            "SINGLE" if font.underline is True else None
        ),
        "font_strikethrough": None,  # python-pptx doesn't fully expose this
        "font_color": font_color,
        "font_color_theme": font_color_theme,
        "font_color_brightness": brightness,
        "is_line_break": False,
        "is_field": False,
        "field_type": None,
        "hyperlink_url": run.hyperlink.address if run.hyperlink and run.hyperlink.address else None,
    })
