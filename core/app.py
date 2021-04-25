from chatbot_service import ChatbotService
import math
import random
from flask import Flask, jsonify, request

app = Flask(__name__)

service = ChatbotService.get_instance()


@app.route("/chat", methods=["POST"])
def hello():
    req = request.json
    res = service.receive(req["id"], req["text"])
    return jsonify(body=res)


@app.route("/image", methods=["POST"])
def image():
    req = request.json
    result = service.receive_image(req["base64"])
    return jsonify(body=result)


@app.route("/ask", methods=["POST"])
def ask():
    req = request.json
    result = service.ask(req["question"])
    return jsonify(body=result)


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)