from flask import Flask, jsonify, request
from text_generator import TextGenerator

app = Flask(__name__)

ai = TextGenerator()


@app.route("/api/generate", methods=["POST"])
def generate():
    req = request.json
    text = req["text"]
    reply = ai.generate_one(text)
    return jsonify(body={"text": reply})

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)