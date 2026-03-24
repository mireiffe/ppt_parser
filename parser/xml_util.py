"""lxml helpers for accessing properties not exposed by python-pptx."""

from lxml import etree

NSMAP = {
    "a": "http://schemas.openxmlformats.org/drawingml/2006/main",
    "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
    "p": "http://schemas.openxmlformats.org/presentationml/2006/main",
}


def xpath(element, path: str):
    """Run an XPath query with common OOXML namespaces.

    python-pptx's BaseOxmlElement overrides xpath() and doesn't accept
    'namespaces', so we use lxml's etree.XPath or findall with Clark notation
    as needed. We try namespaces first (raw lxml elements), then fall back.
    """
    try:
        return element.xpath(path, namespaces=NSMAP)
    except TypeError:
        # python-pptx element: convert path to Clark notation
        clark_path = _to_clark(path)
        results = element.findall(clark_path)
        return results if results is not None else []


def _to_clark(xpath_path: str) -> str:
    """Convert namespace-prefixed XPath to Clark notation for findall().

    Examples:
        ".//a:xfrm" → ".//{http://schemas.openxmlformats.org/drawingml/2006/main}xfrm"
        "a:srgbClr" → "{http://schemas.openxmlformats.org/drawingml/2006/main}srgbClr"
    """
    import re
    def _replace(match):
        prefix = match.group(1)
        local = match.group(2)
        ns = NSMAP.get(prefix)
        if ns:
            return f"{{{ns}}}{local}"
        return match.group(0)
    return re.sub(r"\b([a-z]):([a-zA-Z_]\w*)", _replace, xpath_path)


def get_attrib(element, attr: str, default=None):
    """Get an attribute value, returning default if not present."""
    return element.attrib.get(attr, default)


def get_flip(shape) -> tuple[bool, bool]:
    """Extract flipH/flipV from a shape's XML element."""
    sp = shape._element
    xfrm_list = xpath(sp, ".//a:xfrm") or xpath(sp, ".//p:xfrm")
    if not xfrm_list:
        return False, False
    xfrm = xfrm_list[0]
    flip_h = get_attrib(xfrm, "flipH", "0") == "1"
    flip_v = get_attrib(xfrm, "flipV", "0") == "1"
    return flip_h, flip_v


def get_group_child_transform(shape) -> tuple[int | None, int | None, int | None, int | None]:
    """Extract chOff (x, y) and chExt (cx, cy) from a group shape."""
    sp = shape._element
    ch_off_list = xpath(sp, ".//a:xfrm/a:chOff") or xpath(sp, ".//p:xfrm/a:chOff")
    ch_ext_list = xpath(sp, ".//a:xfrm/a:chExt") or xpath(sp, ".//p:xfrm/a:chExt")
    if not ch_off_list or not ch_ext_list:
        return None, None, None, None
    ch_off = ch_off_list[0]
    ch_ext = ch_ext_list[0]
    return (
        int(ch_off.get("x", 0)),
        int(ch_off.get("y", 0)),
        int(ch_ext.get("cx", 0)),
        int(ch_ext.get("cy", 0)),
    )


def get_line_ends(shape) -> dict:
    """Extract head/tail end properties from a:ln/a:headEnd and a:ln/a:tailEnd."""
    result = {
        "line_head_type": None, "line_head_w": None, "line_head_len": None,
        "line_tail_type": None, "line_tail_w": None, "line_tail_len": None,
    }
    sp = shape._element
    head_list = xpath(sp, ".//a:ln/a:headEnd")
    tail_list = xpath(sp, ".//a:ln/a:tailEnd")
    if head_list:
        h = head_list[0]
        t = h.get("type")
        if t and t != "none":
            result["line_head_type"] = t
            result["line_head_w"] = h.get("w", "med")
            result["line_head_len"] = h.get("len", "med")
    if tail_list:
        t = tail_list[0]
        tt = t.get("type")
        if tt and tt != "none":
            result["line_tail_type"] = tt
            result["line_tail_w"] = t.get("w", "med")
            result["line_tail_len"] = t.get("len", "med")
    return result


def get_shadow_from_xml(shape) -> dict | None:
    """Extract shadow properties directly from XML effectLst/outerShdw."""
    sp = shape._element
    outer_list = xpath(sp, ".//a:effectLst/a:outerShdw")
    if not outer_list:
        return None
    o = outer_list[0]
    blur_rad = o.get("blurRad")
    dist = o.get("dist")
    direction = o.get("dir")

    # Extract color and alpha
    color = None
    alpha = None
    for child in o:
        tag = child.tag.split("}")[-1] if "}" in child.tag else child.tag
        if tag == "srgbClr":
            color = child.get("val")
            alpha_els = xpath(child, "a:alpha")
            if alpha_els:
                alpha = alpha_els[0].get("val")
        elif tag == "schemeClr":
            # We'd need theme resolution here; use black as fallback
            color = "000000"
            alpha_els = xpath(child, "a:alpha")
            if alpha_els:
                alpha = alpha_els[0].get("val")

    data = {"style": "OUTER"}
    if blur_rad:
        data["blur_radius"] = int(blur_rad)
    if dist:
        data["distance"] = int(dist)
    if direction:
        data["direction"] = int(direction)
    if color:
        data["color"] = color
    if alpha:
        # alpha is in 1/1000 percent, e.g. "40000" = 40%
        data["alpha"] = int(alpha) / 100000.0
    return data


def get_fill_alpha(shape) -> float | None:
    """Extract fill transparency/alpha from XML."""
    sp = shape._element
    nsmap = {"a": "http://schemas.openxmlformats.org/drawingml/2006/main"}
    # Check solidFill alpha
    solid = sp.findall(".//a:spPr/a:solidFill", nsmap)
    for s in solid:
        alpha_els = s.findall(".//a:alpha", nsmap)
        if alpha_els:
            val = alpha_els[0].get("val")
            if val:
                return int(val) / 100000.0
    return None


def get_text_direction(shape) -> str | None:
    """Extract text direction (vert attribute) from bodyPr."""
    sp = shape._element
    body_pr_list = xpath(sp, ".//a:bodyPr")
    if not body_pr_list:
        return None
    vert = body_pr_list[0].get("vert")
    if vert is None or vert == "horz":
        return "HORIZONTAL"
    if vert == "vert":
        return "VERTICAL"
    if vert == "vert270":
        return "VERTICAL_270"
    return vert
