# ppt-parser

PPTX 파일을 SQLite로 파싱하고 웹 뷰어로 확인하는 도구.

## 구조

```
parser/     PPTX → SQLite 파서 (python-pptx)
api/        FastAPI 백엔드
frontend/   React + Vite 프론트엔드
```

## 설치

```bash
# Backend
uv sync

# Frontend
cd frontend && npm install
```

## 사용법

### 1. PPTX 파싱

```bash
# 단일 파일
ppt-parse parse input.pptx -o output.db --db-no 0

# 배치 (samples/{db_no}/*.pptx → 하나의 DB)
ppt-parse batch -o samples.db --samples-dir samples
```

### 2. 웹 뷰어 실행

```bash
# API 서버 + 프론트엔드 동시 실행
make dev DB=samples.db
```

개별 실행:

```bash
# Backend (port 8000)
PPTX_DB_PATH=samples.db uvicorn api.main:app --reload

# Frontend (port 5173 → proxy to 8000)
cd frontend && npm run dev
```

## 주요 기술

- **Parser**: python-pptx, lxml, Pillow, Playwright (슬라이드 캡처)
- **Backend**: FastAPI, SQLite
- **Frontend**: React 19, Vite, Chart.js
