from flask import Flask, request, abort, jsonify
import random
import datetime

app = Flask(__name__)

@app.get('/')
def hello_world():
    return "Scrabble Scrabble Scrabble Cats!"
