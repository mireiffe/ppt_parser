"""FastAPI application entry point."""

import argparse
import sys
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .database import set_db_path
from .routers import presentations, slides, media

app = FastAPI(title="PPTX Viewer API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(presentations.router)
app.include_router(slides.router)
app.include_router(media.router)


@app.get("/api/health")
def health():
    return {"status": "ok"}


def main():
    parser = argparse.ArgumentParser(description="PPTX Viewer API Server")
    parser.add_argument("--db", required=True, help="Path to the SQLite database")
    parser.add_argument("--port", type=int, default=8000, help="Server port")
    parser.add_argument("--host", default="0.0.0.0", help="Server host")
    args = parser.parse_args()

    if not Path(args.db).exists():
        print(f"Error: Database not found: {args.db}", file=sys.stderr)
        sys.exit(1)

    set_db_path(args.db)

    import uvicorn
    uvicorn.run(app, host=args.host, port=args.port)


if __name__ == "__main__":
    main()
