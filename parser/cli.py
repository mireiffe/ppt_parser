"""CLI entrypoint: parse a PPTX file into a SQLite database."""

import argparse
import sys
from pathlib import Path

from pptx import Presentation

from .capture import capture_slides
from .db import create_db
from .image import ImageStore
from .presentation import parse_presentation
from .slide import parse_slide_masters, parse_slides
from .theme import parse_themes


def parse_pptx(input_path: str, output_path: str | None = None, db_no: int = 0) -> str:
    """
    Parse a PPTX file into a SQLite database.
    If output_path already exists, appends to the existing DB.
    Returns the output database path.
    """
    input_path = Path(input_path)
    if not input_path.exists():
        raise FileNotFoundError(f"File not found: {input_path}")

    if output_path is None:
        output_path = input_path.with_suffix(".db")
    else:
        output_path = Path(output_path)

    print(f"Parsing: {input_path}")
    print(f"Output:  {output_path}")

    prs = Presentation(str(input_path))
    conn = create_db(output_path)

    try:
        # 1. Presentation metadata
        pres_id = parse_presentation(prs, str(input_path), conn, db_no=db_no)
        print(f"  Presentation: {input_path.name} (db_no={db_no}) ({int(prs.slide_width)/914400:.1f}\" x {int(prs.slide_height)/914400:.1f}\")")

        # 2. Themes
        theme_data = parse_themes(prs, pres_id, conn)
        print(f"  Themes: {len(theme_data)}")

        # 3. Slide masters and layouts (+ master/layout shapes)
        image_store = ImageStore(conn, pres_id)
        layout_map = parse_slide_masters(prs, pres_id, theme_data, conn, image_store)
        print(f"  Layouts: {len(layout_map)}")

        # 4. Slides with shapes
        parse_slides(prs, pres_id, layout_map, conn, image_store)
        print(f"  Slides: {len(prs.slides)}")

        conn.commit()

        # 5. Capture slide images (high-quality)
        try:
            img_count = capture_slides(input_path, conn, scale=2.0)
            conn.commit()
            print(f"  Slide images: {img_count} captured")
        except Exception as e:
            print(f"  Slide images: capture failed ({e})")

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


def batch_parse(samples_dir: str, output_path: str) -> str:
    """
    Parse all samples/{db_no}/*.pptx into one shared .db file.
    Discovers db_no from subdirectory names.
    """
    samples_dir = Path(samples_dir)
    output_path = Path(output_path)

    if output_path.exists():
        output_path.unlink()

    count = 0
    for subdir in sorted(samples_dir.iterdir(), key=lambda p: int(p.name) if p.name.isdigit() else 0):
        if not subdir.is_dir():
            continue
        try:
            db_no = int(subdir.name)
        except ValueError:
            continue
        for pptx_file in sorted(subdir.glob("*.pptx")):
            parse_pptx(str(pptx_file), str(output_path), db_no=db_no)
            count += 1

    print(f"\nBatch complete: {count} presentations parsed into {output_path}")
    return str(output_path)


def main():
    parser = argparse.ArgumentParser(
        description="Parse PPTX file(s) into a SQLite database."
    )
    sub = parser.add_subparsers(dest="command")

    # Single file parse
    single = sub.add_parser("parse", help="Parse a single PPTX file")
    single.add_argument("input", help="Path to the .pptx file")
    single.add_argument("-o", "--output", help="Output .db file path (default: same name as input)")
    single.add_argument("--db-no", type=int, required=True, help="Unique presentation number (PK)")

    # Batch parse
    batch = sub.add_parser("batch", help="Batch-parse all samples/{db_no}/*.pptx")
    batch.add_argument("--samples-dir", default="samples", help="Path to samples directory")
    batch.add_argument("-o", "--output", required=True, help="Output .db file path")

    args = parser.parse_args()

    try:
        if args.command == "batch":
            batch_parse(args.samples_dir, args.output)
        elif args.command == "parse":
            parse_pptx(args.input, args.output, db_no=args.db_no)
        else:
            parser.print_help()
            sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
