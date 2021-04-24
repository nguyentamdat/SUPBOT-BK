from flask import Flask, jsonify, request
from aitextgen import aitextgen

app = Flask(__name__)

ai = aitextgen(model_folder="trained_model", tokenizer_file="aitextgen.tokenizer.json")


@app.route("/api/generate", methods=["POST"])
def generate():
    req = request.json
    text = req["text"]
    reply = ai.generate_one(
        prompt=text + "\n", temperature=1.0, top_p=0.9, top_k=20
    ).split("\n")[1]
    return jsonify(body={"text": reply})
