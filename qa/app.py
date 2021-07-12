import uvicorn
from qa_system import QAAgent
from fastapi import FastAPI
from pydantic import BaseModel
from typing import List

app = FastAPI()

qa = QAAgent()

class Text(BaseModel):
    question: str


@app.post("/ask")
def ask(data: Text):
    data = data.dict()
    text = data["question"]
    reply = qa.get_answer(text)
    return {"answer": reply}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=5000)