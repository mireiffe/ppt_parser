"""Parse theme colors and fonts from slide masters."""

import sqlite3

from pptx import Presentation

from .db import insert_row
from .xml_util import xpath

# clrScheme child tag → DB column mapping
_CLR_TAGS = {
    "dk1": "clr_dk1", "lt1": "clr_lt1",
    "dk2": "clr_dk2", "lt2": "clr_lt2",
    "accent1": "clr_accent1", "accent2": "clr_accent2",
    "accent3": "clr_accent3", "accent4": "clr_accent4",
    "accent5": "clr_accent5", "accent6": "clr_accent6",
    "hlink": "clr_hlink", "folHlink": "clr_folhlink",
}


def _extract_color_hex(color_elem) -> str | None:
    """Extract #RRGGBB from a theme color element (srgbClr or sysClr)."""
    # <a:srgbClr val="4472C4"/>
    srgb = xpath(color_elem, "a:srgbClr")
    if srgb:
        val = srgb[0].get("val", "")
        if len(val) == 6:
            return f"#{val.upper()}"

    # <a:sysClr val="windowText" lastClr="000000"/>
    sys_clr = xpath(color_elem, "a:sysClr")
    if sys_clr:
        last_clr = sys_clr[0].get("lastClr", "")
        if len(last_clr) == 6:
            return f"#{last_clr.upper()}"

    return None


def parse_themes(prs: Presentation, pres_id: int, conn: sqlite3.Connection) -> dict[int, dict]:
    """
    Parse themes from slide masters.
    Returns {slide_master_index: {theme_id, colors_dict}}.
    """
    result = {}

    for idx, master in enumerate(prs.slide_masters):
        theme_elem = master.element
        theme_name = None
        colors = {}

        # Find clrScheme
        clr_schemes = xpath(theme_elem, ".//a:clrScheme")
        if clr_schemes:
            scheme = clr_schemes[0]
            theme_name = scheme.get("name")
            for tag, col in _CLR_TAGS.items():
                elems = xpath(scheme, f"a:{tag}")
                if elems:
                    colors[col] = _extract_color_hex(elems[0])

        # Find fontScheme
        fonts = {}
        font_schemes = xpath(theme_elem, ".//a:fontScheme")
        if font_schemes:
            fs = font_schemes[0]
            for kind in ("majorFont", "minorFont"):
                font_elems = xpath(fs, f"a:{kind}")
                if font_elems:
                    latin = xpath(font_elems[0], "a:latin")
                    ea = xpath(font_elems[0], "a:ea")
                    prefix = "font_major" if kind == "majorFont" else "font_minor"
                    if latin:
                        fonts[f"{prefix}_latin"] = latin[0].get("typeface")
                    if ea:
                        fonts[f"{prefix}_ea"] = ea[0].get("typeface")

        row_data = {"presentation_id": pres_id, "name": theme_name}
        row_data.update(colors)
        row_data.update(fonts)
        theme_id = insert_row(conn, "themes", row_data)

        result[idx] = {"theme_id": theme_id, "colors": colors}

    return result
