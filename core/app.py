from core.chatbot_service import ChatbotService
import math
import random
from flask import Flask, jsonify, request
app = Flask(__name__)

service = ChatbotService.get_instance()


@app.route('/domain', methods=["POST"])
def hello():
    req = request.json
    res = service.receive(req['id'], req['text'])
    return jsonify(body=res)


@app.route('/whichbot', methods=["POST"])
def choose_bot():
    return jsonify(body="hello", intent="bot"+str(round(random.random())))

@app.route('/image', methods=["POST"])
def image():
    req = request.json
    result = service.receive_image(req['base64'])
    return jsonify(body=result)
