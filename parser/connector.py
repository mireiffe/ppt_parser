"""Connector shape parsing (handled in shape.py, this module is reserved for extensions)."""

# Connector parsing is integrated into shape.py since python-pptx exposes
# begin_x, begin_y, end_x, end_y directly on connector shapes.
# This module exists for future extensions (e.g., routing/elbow connectors).
