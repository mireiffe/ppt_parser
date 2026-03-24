"""CLI entrypoint: parse a PPTX file into a SQLite database."""

import argparse
import sys
from pathlib import Path

from pptx import Presentation

from .db import create_db
from .image import ImageStore
from .presentation import parse_presentation
from .slide import parse_slide_masters, parse_slides
from .theme import parse_themes


def parse_pptx(input_path: str, output_path: str | None = None) -> str:
    """
    Parse a PPTX file into a SQLite database.
    Returns the output database path.
    """
    input_path = Path(input_path)
    if not input_path.exists():
        raise FileNotFoundError(f"File not found: {input_path}")

    if output_path is None:
        output_path = input_path.with_suffix(".db")
    else:
        output_path = Path(output_path)

    # Remove existing DB to start fresh
    if output_path.exists():
        output_path.unlink()

    print(f"Parsing: {input_path}")
    print(f"Output:  {output_path}")

    prs = Presentation(str(input_path))
    conn = create_db(output_path)

    try:
        # 1. Presentation metadata
        pres_id = parse_presentation(prs, str(input_path), conn)
        print(f"  Presentation: {input_path.name} ({int(prs.slide_width)/914400:.1f}\" x {int(prs.slide_height)/914400:.1f}\")")

        # 2. Themes
        theme_data = parse_themes(prs, pres_id, conn)
        print(f"  Themes: {len(theme_data)}")

        # 3. Slide masters and layouts
        layout_map = parse_slide_masters(prs, pres_id, theme_data, conn)
        print(f"  Layouts: {len(layout_map)}")

        # 4. Slides with shapes
        image_store = ImageStore(conn, pres_id)
        parse_slides(prs, pres_id, layout_map, conn, image_store)
        print(f"  Slides: {len(prs.slides)}")

        conn.commit()

        # Summary
        cur = conn.execute("SELECT COUNT(*) FROM shapes")
        shape_count = cur.fetchone()[0]
        cur = conn.execute("SELECT COUNT(*) FROM media")
        media_count = cur.fetchone()[0]
        cur = conn.execute("SELECT COUNT(*) FROM runs")
        run_count = cur.fetchone()[0]
        print(f"  Shapes: {shape_count}, Media: {media_count}, Text runs: {run_count}")
        print("Done.")

    finally:
        conn.close()

    return str(output_path)


def main():
    parser = argparse.ArgumentParser(
        description="Parse a PPTX file into a SQLite database."
    )
    parser.add_argument("input", help="Path to the .pptx file")
    parser.add_argument("-o", "--output", help="Output .db file path (default: same name as input)")
    args = parser.parse_args()

    try:
        parse_pptx(args.input, args.output)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
