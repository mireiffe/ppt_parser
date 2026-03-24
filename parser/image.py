"""Extract images from shapes and deduplicate by SHA1."""

import hashlib
import sqlite3

from .db import insert_row


class ImageStore:
    """Manages image deduplication during parsing."""

    def __init__(self, conn: sqlite3.Connection, pres_id: int):
        self.conn = conn
        self.pres_id = pres_id
        self._hash_to_id: dict[str, int] = {}

    def store_image(self, blob: bytes, filename: str | None, content_type: str | None) -> int:
        """Store image blob, returning media_id. Deduplicates by SHA1."""
        sha1 = hashlib.sha1(blob).hexdigest()

        if sha1 in self._hash_to_id:
            return self._hash_to_id[sha1]

        media_id = insert_row(self.conn, "media", {
            "presentation_id": self.pres_id,
            "filename": filename,
            "content_type": content_type,
            "sha1": sha1,
            "data": blob,
        })
        self._hash_to_id[sha1] = media_id
        return media_id

    def get_media_id(self, shape) -> int | None:
        """Extract and store image from a picture shape."""
        try:
            image = shape.image
            blob = image.blob
            filename = image.filename if hasattr(image, "filename") else None
            content_type = image.content_type
            return self.store_image(blob, filename, content_type)
        except Exception:
            return None
