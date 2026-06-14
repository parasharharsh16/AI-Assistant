from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

from .assistant import JarvisAssistant

app = FastAPI(title="Jarvis Assistant")
assistant = JarvisAssistant()

app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/", response_class=HTMLResponse)
async def index():
    with open("static/index.html", encoding="utf-8") as f:
        return f.read()


@app.post("/api/chat")
async def chat(request: Request):
    payload = await request.json()
    message = payload.get("message", "").strip()
    if not message:
        return {"error": "Message cannot be empty."}

    response = assistant.reply(message)
    return {"response": response}
