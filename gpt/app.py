import uvicorn
from text_generator import TextGenerator
from fastapi import FastAPI
from pydantic import BaseModel
from typing import List

app = FastAPI()

ai = TextGenerator()


class Text(BaseModel):
    text: List[str]


@app.post("/generate")
def generate(data: Text):
    data = data.dict()
    print(data["text"][:-3])
    text = data["text"][:-3]
    text = "\n".join(text)
    idx = len(text)
    reply = ai.generate_one(text, idx)
    return {"text": reply}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=5000)