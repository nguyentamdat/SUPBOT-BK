import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel
from chatbot_service import ChatbotService
import math
import random

app = FastAPI()

service = ChatbotService.get_instance()


class Chat(BaseModel):
    id: str
    text: str


class Image(BaseModel):
    base64: str


class Ask(BaseModel):
    question: str


@app.get("/")
def index():
    return "Multi chatbot backend AI"


@app.post("/chat")
def chat():
    req = request.json
    res = service.receive(req["id"], req["text"])
    return res


@app.post("/image")
def image():
    req = request.json
    result = service.receive_image(req["base64"])
    return result


@app.post("/ask")
def ask():
    req = request.json
    result = service.ask(req["question"])
    return result


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=5000)