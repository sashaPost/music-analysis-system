# 🎵 Music Analysis System

This is a Python-based backend system for analyzing user music taste and generating smart music recommendations via AI and streaming platform integrations.

---

## 🚀 Features

- User data ingestion (planned Spotify integration)
- Track/artist/genre database
- AI-driven preference analysis and suggestion engine (WIP)
- Clean modular FastAPI backend
- Async SQLAlchemy + PostgreSQL + Redis
- Pytest-based test suite with isolated test DB

---

## ⚙️ Installation & Setup

### 1. Clone and set up your environment

```bash
git clone <your-repo-url>
cd music-analysis-system

python -m venv venv
source venv/bin/activate
pip install -e .[dev]
```

### 2. Start backend services (DB + Redis)

```bash
docker compose up -d db redis
```

### 3. Set up your `.env.dev` in the project root

See [`.env.example`](.env.example) for all available variables.

Make sure it looks like this (Linux/Docker-friendly):

```env
DATABASE_URL=postgresql+asyncpg://postgres:password@172.17.0.1:5432/music_analysis
REDIS_URL=redis://172.17.0.1:6379
SECRET_KEY=super-secret-key-must-be-16+chars

API_V1_PREFIX=/api/v1
DEBUG=True

SPOTIFY_CLIENT_ID=your-spotify-client-id
SPOTIFY_CLIENT_SECRET=your-spotify-client-secret

MODEL_PATH=./data/models/
BATCH_SIZE=32
EPOCHS=100
```

> ✅ Ensure the file is named `.env.dev` — not `env.dev`!

---

### 4. Prepare the database

Create the test DB:
```bash
python scripts/create_test_db.py
```

Create the main schema:
```bash
python scripts/setup_db.py
```

---

### 5. Run the API server

```bash
uvicorn app.main:app --reload
```

Visit [http://localhost:8000/docs](http://localhost:8000/docs) for the auto-generated Swagger UI.

---

## 🧪 Running Tests

Run tests with `pytest` and the isolated test DB:

```bash
# make sure Docker DB is running and .env.dev is present
python scripts/create_test_db.py
pytest tests/ -v
```

> Test route paths are based on the prefix `/api/v1`.

---

## 🧠 Route Structure

All routes live under `/api/v1`:

- `GET /api/v1/debug/env` — debug environment dump
- `GET /api/v1/tracks/`, `POST /api/v1/upload/spotify`, etc.

---

## 📦 Project Structure

```
app/
├── api/           # FastAPI route modules
│   └── routes/    # Grouped routers (users, tracks, data, etc.)
├── services/      # Business logic modules
├── db/            # SQLAlchemy models & database engine
├── schemas/       # Pydantic schemas
├── config.py      # Pydantic settings loader
├── main.py        # FastAPI app entrypoint
tests/
├── api/           # Route-level tests
├── services/      # Logic-level tests
├── conftest.py    # Async client and DB fixtures
scripts/
├── setup_db.py    # Initializes all tables
├── create_test_db.py  # Ensures test DB exists
```

---

## 🧰 Development Notes

- Uses `asyncpg` driver for true async PostgreSQL
- Switchable environments via `ENV=dev` / `prod` / `test`
- Debug route introspection on startup (via `lifespan`)