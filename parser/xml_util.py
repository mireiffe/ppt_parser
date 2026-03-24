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
