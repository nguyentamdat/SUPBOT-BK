import uvicorn
from text_generator import TextGenerator
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

ai = TextGenerator()


class Text(BaseModel):
    text: str


@app.post("/generate")
def generate(data: Text):
    data = data.dict()
    text = data["text"]
    reply = ai.generate_one(text)
    return {"text": reply}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=5000)