from flask import Flask, request, jsonify, render_template
import json, os, uuid
from datetime import datetime

app = Flask(__name__)
DB_FILE = "data.json"

def load_db():
    if not os.path.exists(DB_FILE):
        return {"hardware": [], "employees": [], "trash": []}
    with open(DB_FILE) as f:
        return json.load(f)

def save_db(data):
    with open(DB_FILE, "w") as f:
        json.dump(data, f, indent=2)

def init_db():
    if not os.path.exists(DB_FILE):
        sample = {
            "hardware": [
                {"id":"HW001","type":"Laptop","brand":"Dell","model":"