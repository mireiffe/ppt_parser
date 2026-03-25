DB       ?= samples.db
API_PORT ?= 8000
FE_PORT  ?= 5173

.PHONY: dev api frontend

dev:
	@if [ ! -f "$(DB)" ]; then echo "Error: DB file '$(DB)' not found"; exit 1; fi
	@trap 'kill 0' EXIT; \
	PPTX_DB_PATH=$(DB) uv run uvicorn api.main:app --reload --port $(API_PORT) & \
	API_PORT=$(API_PORT) npm --prefix frontend run dev -- --port $(FE_PORT) & \
	wait

api:
	PPTX_DB_PATH=$(DB) uv run uvicorn api.main:app --reload --port $(API_PORT)

frontend:
	API_PORT=$(API_PORT) npm --prefix frontend run dev -- --port $(FE_PORT)
