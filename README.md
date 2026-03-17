# fastapi-demo

FastAPI service for generating Django ORM queries from natural language using a LangChain agent + Chroma vector retrieval.

Project source lives in `ai-chatbot/`.

## Features

- Natural language to Django ORM query generation
- API-key based multi-project access
- Query history and project stats
- Batch query generation
- Tortoise ORM models with Aerich migrations
- Chroma-backed schema/example retrieval for agent context

## Tech Stack

- FastAPI
- Tortoise ORM + Aerich
- PostgreSQL
- LangChain + OpenAI-compatible chat API
- ChromaDB + sentence-transformers
- `uv` for dependency management

## Project Layout

```text
fastapi-demo/
└── ai-chatbot/
    ├── main.py
    ├── pyproject.toml
    ├── aerich.ini
    ├── core/
    └── apps/ai_agent/
```

## Prerequisites

- Python 3.11+
- PostgreSQL
- `uv` (recommended)

## Quick Start

1. Move into the app directory:

```bash
cd ai-chatbot
```

2. Create and sync environment:

```bash
uv venv
uv sync
```

3. Create environment file:

```bash
cp .env.example .env
```

4. Update required values in `.env`:

- `DATABASE_URL`
- `AI_API_KEY`
- `AI_API_BASE_URL`
- `AI_MODEL`

5. Run database migrations:

```bash
uv run aerich upgrade
```

If migrations are not initialized yet in your environment:

```bash
uv run aerich init -t core.config:TORTOISE_ORM
uv run aerich init-db
```

6. Start the API:

```bash
uv run uvicorn main:app --reload
```

## API Docs

- Swagger UI: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`

## Core Endpoints

Health:

- `GET /`
- `GET /health`

Project management:

- `POST /ai_agent/projects`
- `GET /ai_agent/projects`
- `GET /ai_agent/projects/{project_id}`
- `POST /ai_agent/projects/{project_id}/regenerate-key`
- `DELETE /ai_agent/projects/{project_id}`

Query APIs (require `X-API-Key`):

- `POST /ai_agent/query`
- `POST /ai_agent/query/batch`
- `GET /ai_agent/history`
- `GET /ai_agent/history/{query_id}`
- `GET /ai_agent/stats`

## Example Usage

1. Create a project (returns API key):

```bash
curl -X POST http://127.0.0.1:8000/ai_agent/projects \
  -H "Content-Type: application/json" \
  -d '{"name":"demo-project","description":"Local testing"}'
```

2. Generate an ORM query:

```bash
curl -X POST http://127.0.0.1:8000/ai_agent/query \
  -H "Content-Type: application/json" \
  -H "X-API-Key: sk_proj_your_key_here" \
  -d '{
    "query": "List all active users created this month",
    "include_explanation": true,
    "include_metadata": true
  }'
```

## Optional: Build Vector Collections

Data files are stored in:

- `apps/ai_agent/ejl_data/schema`
- `apps/ai_agent/ejl_data/fewshot`

Build vectors from pipeline scripts (run from `ai-chatbot/`):

```bash
cd apps/ai_agent
python pipeline/create_vectors.py
```

Note: in `create_vectors.py`, only `fewshot_vec` is enabled by default; enable schema build as needed.

## Notes

- Admin/project endpoints are currently unprotected; add admin auth before production use.
- Query endpoints enforce API key format `sk_proj_...` and active project validation.
- Existing `ai-chatbot/README.md` appears to be legacy boilerplate and does not match this implementation.
