import uvicorn
from text_generator import TextGenerator
from fastapi import FastAPI
from pydantic import BaseModel
from typing import List

app = FastAPI()

ai = TextGenerator()


class Text(BaseModel):
    text: List[str]
    num: int


@app.post("/generate")
def generate(data: Text):
    data = data.dict()
    # print(data)
    num = data["num"]
    text = data["text"][-num:]
    idx = len(text)
    # print(data["text"][-3:])
    text = "\n".join(text)
    reply = ai.generate_one(text, idx)
    # print(reply)
    return {"text": reply}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=5000)