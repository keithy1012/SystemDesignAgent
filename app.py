from flask import Flask, render_template, request, jsonify, session
from agent.architect_agent import clarify_once, generate_system_design
import json
import os
from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")

@app.route("/")
def home():
    session["conversation"] = []
    return render_template("index.html")

@app.route("/chat/send", methods=["POST"])
def chat_send():
    user_message = request.json.get("message")
    conversation = session.get("conversation", [])
    conversation.append({"role": "user", "content": user_message})

    response = clarify_once(conversation)

    session["conversation"] = conversation

    if response.get("ready"):
        session["conversation"].append({"role": "assistant", "content": response["summary"]})
        design = generate_system_design(session["conversation"])
        return jsonify({"ready": True, "summary": response["summary"], "design": design})

    return jsonify({"ready": False, "question": response.get("question", "Can you clarify further?")})
