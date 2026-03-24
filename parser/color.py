"""Theme color resolution: theme color enum → #RRGGBB hex."""

from pptx.dml.color import RGBColor
from pptx.enum.dml import MSO_THEME_COLOR


# Mapping from MSO_THEME_COLOR enum to theme table column names
THEME_COLOR_MAP = {
    MSO_THEME_COLOR.DARK_1: "clr_dk1",
    MSO_THEME_COLOR.LIGHT_1: "clr_lt1",
    MSO_THEME_COLOR.DARK_2: "clr_dk2",
    MSO_THEME_COLOR.LIGHT_2: "clr_lt2",
    MSO_THEME_COLOR.ACCENT_1: "clr_accent1",
    MSO_THEME_COLOR.ACCENT_2: "clr_accent2",
    MSO_THEME_COLOR.ACCENT_3: "clr_accent3",
    MSO_THEME_COLOR.ACCENT_4: "clr_accent4",
    MSO_THEME_COLOR.ACCENT_5: "clr_accent5",
    MSO_THEME_COLOR.ACCENT_6: "clr_accent6",
    MSO_THEME_COLOR.HYPERLINK: "clr_hlink",
    MSO_THEME_COLOR.FOLLOWED_HYPERLINK: "clr_folhlink",
}


def _apply_brightness(r: int, g: int, b: int, brightness: float) -> tuple[int, int, int]:
    """Apply tint (positive) or shade (negative) to an RGB color."""
    if brightness > 0:
        # Tint: blend toward white
        r = int(r + (255 - r) * brightness)
        g = int(g + (255 - g) * brightness)
        b = int(b + (255 - b) * brightness)
    elif brightness < 0:
        # Shade: blend toward black
        factor = 1.0 + brightness  # e.g., -0.25 → factor 0.75
        r = int(r * factor)
        g = int(g * factor)
        b = int(b * factor)
    return (
        max(0, min(255, r)),
        max(0, min(255, g)),
        max(0, min(255, b)),
    )


def hex_from_rgb(rgb: RGBColor | None) -> str | None:
    """Convert RGBColor to '#RRGGBB' string."""
    if rgb is None:
        return None
    return f"#{rgb[0]:02X}{rgb[1]:02X}{rgb[2]:02X}"


def resolve_color(color_format, theme_colors: dict | None = None) -> tuple[str | None, str | None, float | None]:
    """
    Resolve a ColorFormat object to (#RRGGBB, theme_name, brightness).

    Returns (resolved_hex, theme_color_name, brightness).
    """
    if color_format is None:
        return None, None, None

    try:
        color_type = color_format.type
    except (AttributeError, TypeError):
        return None, None, None

    if color_type is None:
        return None, None, None

    # Direct RGB color
    from pptx.enum.dml import MSO_COLOR_TYPE
    if color_type == MSO_COLOR_TYPE.RGB:
        return hex_from_rgb(color_format.rgb), None, None

    # Theme/scheme color
    if color_type == MSO_COLOR_TYPE.SCHEME:
        theme_color_enum = color_format.theme_color
        brightness = color_format.brightness if color_format.brightness else 0.0
        theme_col_name = THEME_COLOR_MAP.get(theme_color_enum)
        theme_name_str = theme_color_enum.name if theme_color_enum else None

        resolved_hex = None
        if theme_colors and theme_col_name and theme_col_name in theme_colors:
            base_hex = theme_colors[theme_col_name]
            if base_hex and base_hex.startswith("#") and len(base_hex) == 7:
                r = int(base_hex[1:3], 16)
                g = int(base_hex[3:5], 16)
                b = int(base_hex[5:7], 16)
                r, g, b = _apply_brightness(r, g, b, brightness)
                resolved_hex = f"#{r:02X}{g:02X}{b:02X}"

        return resolved_hex, theme_name_str, brightness if brightness else None

    return None, None, None
