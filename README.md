# Jarvis Assistant

A locally hosted Jarvis-style assistant scaffolded for small-model memory optimization.

## What this project includes

- `FastAPI` server for a local assistant API
- `sentence-transformers` embeddings for memory-based context retrieval
- `transformers` generation with a lightweight local model
- SQLite-backed vector memory store
- Native desktop UI using Tkinter
- Simple static web UI for local chat
- Scripts to run locally and build via Docker

## Setup

1. Create a Python virtual environment

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

2. Run the web app locally

```powershell
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

3. Open the web assistant UI

Visit `http://127.0.0.1:8000` in your browser.

### Native desktop UI

To run the native desktop version instead of the browser UI:

```powershell
python -m app.desktop
```

Or use the provided script:

```powershell
scripts\run_desktop.ps1
```

## Model configuration

The default text generation model is `google/flan-t5-small`, a smaller open-source model designed for local use.
The embedding model is `sentence-transformers/all-MiniLM-L6-v2` to keep memory and compute requirements low.

To customize the models, set environment variables in a `.env` file or modify `app/config.py`:

```text
MODEL_NAME=google/flan-t5-small
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
```

## Memory

The assistant stores recent interactions in `data/memory.db` and uses semantic search to retrieve the most relevant memories for each response.

## Run scripts

- Web server on Windows PowerShell: `scripts\run.ps1`
- Web server on macOS/Linux: `bash scripts/run.sh`
- Native desktop UI on Windows PowerShell: `scripts\run_desktop.ps1`
- Native desktop UI on macOS/Linux: `bash scripts/run_desktop.sh`

## Build with Docker

```powershell
docker build -t jarvis-assistant .
docker run --rm -p 8000:8000 jarvis-assistant
```
