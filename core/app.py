import math
import random
from flask import Flask, jsonify
from ml_core.domain_classifier import DomainClassifier
app = Flask(__name__)

@app.route('/')
def hello():
    return jsonify(body="Hello from multibot!")

@app.route('/whichbot', methods=["POST"])
def choose_bot():
    return jsonify(body="hello", intent="bot"+str(round(random.random())))

if __name__ == '__main__':
    a = DomainClassifier.instance()
    b = DomainClassifier.instance()
    print(a is b)
    print(a.predict("abc"))
    app.run()