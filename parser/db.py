"""SQLite schema creation and insert helpers."""

import sqlite3
from pathlib import Path

SCHEMA_SQL = """
-- Presentation metadata
CREATE TABLE IF NOT EXISTS presentations (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    filename      TEXT NOT NULL,
    slide_width   INTEGER NOT NULL,   -- EMU (1 inch = 914400)
    slide_height  INTEGER NOT NULL,   -- EMU
    created_at    TEXT DEFAULT (datetime('now'))
);

-- Theme colors and fonts
CREATE TABLE IF NOT EXISTS themes (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    presentation_id INTEGER NOT NULL REFERENCES presentations(id),
    name            TEXT,
    clr_dk1     TEXT, clr_lt1     TEXT,
    clr_dk2     TEXT, clr_lt2     TEXT,
    clr_accent1 TEXT, clr_accent2 TEXT,
    clr_accent3 TEXT, clr_accent4 TEXT,
    clr_accent5 TEXT, clr_accent6 TEXT,
    clr_hlink   TEXT, clr_folhlink TEXT,
    font_major_latin TEXT,
    font_minor_latin TEXT,
    font_major_ea    TEXT,
    font_minor_ea    TEXT
);

-- Slide masters
CREATE TABLE IF NOT EXISTS slide_masters (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    presentation_id INTEGER NOT NULL REFERENCES presentations(id),
    theme_id        INTEGER REFERENCES themes(id),
    name            TEXT,
    bg_fill_type    TEXT,
    bg_fill_color   TEXT,
    bg_fill_json    TEXT
);

-- Slide layouts
CREATE TABLE IF NOT EXISTS slide_layouts (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    slide_master_id INTEGER NOT NULL REFERENCES slide_masters(id),
    name            TEXT,
    layout_type     TEXT,
    bg_fill_type    TEXT,
    bg_fill_color   TEXT,
    bg_fill_json    TEXT
);

-- Slides
CREATE TABLE IF NOT EXISTS slides (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    presentation_id INTEGER NOT NULL REFERENCES presentations(id),
    slide_layout_id INTEGER REFERENCES slide_layouts(id),
    slide_number    INTEGER NOT NULL,
    name            TEXT,
    bg_fill_type    TEXT,
    bg_fill_color   TEXT,
    bg_fill_json    TEXT
);

-- Slide notes
CREATE TABLE IF NOT EXISTS slide_notes (
    id       INTEGER PRIMARY KEY AUTOINCREMENT,
    slide_id INTEGER NOT NULL UNIQUE REFERENCES slides(id),
    text     TEXT NOT NULL DEFAULT ''
);

-- Shapes (all shape types in one table)
CREATE TABLE IF NOT EXISTS shapes (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    slide_id         INTEGER REFERENCES slides(id),
    slide_master_id  INTEGER REFERENCES slide_masters(id),
    slide_layout_id  INTEGER REFERENCES slide_layouts(id),

    shape_type       TEXT NOT NULL,
    name             TEXT,
    preset_geometry  TEXT,

    pos_x    INTEGER,  pos_y   INTEGER,
    width    INTEGER,  height  INTEGER,
    rotation REAL DEFAULT 0,
    flip_h   BOOLEAN DEFAULT 0,
    flip_v   BOOLEAN DEFAULT 0,

    z_order          INTEGER NOT NULL DEFAULT 0,
    parent_group_id  INTEGER REFERENCES shapes(id),

    placeholder_type TEXT,
    placeholder_idx  INTEGER,

    fill_type    TEXT,
    fill_color   TEXT,
    fill_opacity REAL,
    fill_json    TEXT,

    line_color      TEXT,
    line_width      INTEGER,
    line_dash_style TEXT,
    line_opacity    REAL,

    shadow_json     TEXT,

    media_id    INTEGER REFERENCES media(id),
    crop_left   INTEGER,  crop_top    INTEGER,
    crop_right  INTEGER,  crop_bottom INTEGER,

    begin_x INTEGER, begin_y INTEGER,
    end_x   INTEGER, end_y   INTEGER,

    group_ch_off_x  INTEGER, group_ch_off_y  INTEGER,
    group_ch_ext_cx INTEGER, group_ch_ext_cy INTEGER,

    hyperlink_url TEXT,
    raw_xml_snippet TEXT
);

-- Text frames
CREATE TABLE IF NOT EXISTS text_frames (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    shape_id        INTEGER NOT NULL REFERENCES shapes(id),
    word_wrap       BOOLEAN DEFAULT 1,
    auto_size       TEXT,
    margin_left     INTEGER,
    margin_right    INTEGER,
    margin_top      INTEGER,
    margin_bottom   INTEGER,
    vertical_anchor TEXT,
    text_direction  TEXT
);

-- Paragraphs
CREATE TABLE IF NOT EXISTS paragraphs (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    text_frame_id   INTEGER NOT NULL REFERENCES text_frames(id),
    paragraph_index INTEGER NOT NULL,
    alignment       TEXT,
    level           INTEGER DEFAULT 0,
    space_before    INTEGER,
    space_after     INTEGER,
    line_spacing    REAL,
    line_spacing_rule TEXT,
    bullet_type     TEXT,
    bullet_char     TEXT,
    bullet_color    TEXT,
    bullet_size_pct REAL,
    indent          INTEGER,
    margin_left     INTEGER
);

-- Runs (text segments with formatting)
CREATE TABLE IF NOT EXISTS runs (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    paragraph_id   INTEGER NOT NULL REFERENCES paragraphs(id),
    run_index      INTEGER NOT NULL,
    text           TEXT NOT NULL DEFAULT '',
    font_name      TEXT,
    font_size      INTEGER,   -- centi-points: 1800 = 18pt
    font_bold      BOOLEAN,
    font_italic    BOOLEAN,
    font_underline TEXT,
    font_strikethrough TEXT,
    font_color         TEXT,
    font_color_theme   TEXT,
    font_color_brightness REAL,
    is_line_break  BOOLEAN DEFAULT 0,
    is_field       BOOLEAN DEFAULT 0,
    field_type     TEXT,
    hyperlink_url  TEXT
);

-- Table dimensions
CREATE TABLE IF NOT EXISTS table_dimensions (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    shape_id         INTEGER NOT NULL UNIQUE REFERENCES shapes(id),
    num_rows         INTEGER NOT NULL,
    num_cols         INTEGER NOT NULL,
    col_widths_json  TEXT NOT NULL,
    row_heights_json TEXT NOT NULL
);

-- Table cells
CREATE TABLE IF NOT EXISTS table_cells (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    shape_id        INTEGER NOT NULL REFERENCES shapes(id),
    row_idx         INTEGER NOT NULL,
    col_idx         INTEGER NOT NULL,
    row_span        INTEGER DEFAULT 1,
    col_span        INTEGER DEFAULT 1,
    is_merge_origin BOOLEAN DEFAULT 1,
    fill_type       TEXT,
    fill_color      TEXT,
    margin_left     INTEGER, margin_right  INTEGER,
    margin_top      INTEGER, margin_bottom INTEGER,
    vertical_anchor TEXT,
    border_left_color   TEXT, border_left_width   INTEGER,
    border_right_color  TEXT, border_right_width  INTEGER,
    border_top_color    TEXT, border_top_width    INTEGER,
    border_bottom_color TEXT, border_bottom_width INTEGER,
    text_frame_id   INTEGER REFERENCES text_frames(id)
);

-- Media (images as BLOBs)
CREATE TABLE IF NOT EXISTS media (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    presentation_id INTEGER NOT NULL REFERENCES presentations(id),
    filename        TEXT,
    content_type    TEXT,
    sha1            TEXT,
    data            BLOB NOT NULL
);

-- Indexes for common queries
CREATE INDEX IF NOT EXISTS idx_shapes_slide ON shapes(slide_id);
CREATE INDEX IF NOT EXISTS idx_text_frames_shape ON text_frames(shape_id);
CREATE INDEX IF NOT EXISTS idx_paragraphs_tf ON paragraphs(text_frame_id);
CREATE INDEX IF NOT EXISTS idx_runs_paragraph ON runs(paragraph_id);
CREATE INDEX IF NOT EXISTS idx_table_cells_shape ON table_cells(shape_id);
CREATE INDEX IF NOT EXISTS idx_slides_presentation ON slides(presentation_id);
"""


def create_db(db_path: str | Path) -> sqlite3.Connection:
    """Create a new database with the schema and return the connection."""
    conn = sqlite3.connect(str(db_path))
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    conn.executescript(SCHEMA_SQL)
    conn.commit()
    return conn


def insert_row(conn: sqlite3.Connection, table: str, data: dict) -> int:
    """Insert a row and return the new row id."""
    cols = list(data.keys())
    placeholders = ", ".join(["?"] * len(cols))
    col_names = ", ".join(cols)
    values = [data[c] for c in cols]
    cur = conn.execute(
        f"INSERT INTO {table} ({col_names}) VALUES ({placeholders})", values
    )
    return cur.lastrowid
