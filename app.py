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
    return render_template("index.html")

@app.route("/chat")
def chat():
    session["conversation"] = []
    return render_template("chat.html")

@app.route("/chat/send", methods=["POST"])
def chat_send():
    user_message = request.json.get("message")
    conversation = session.get("conversation", [])

    conversation.append({"role": "user", "content": user_message})

    response = clarify_once(conversation)

    # Save updated conversation
    session["conversation"] = conversation

    # If ready, store conversation and tell frontend to redirect
    if response.get("ready"):
        session["conversation"].append({"role": "assistant", "content": response["summary"]})
        design = generate_system_design(session["conversation"])
        session["design"] = design
        return jsonify({"ready": True, "summary": response["summary"]})

    # Otherwise, return next question
    return jsonify({"ready": False, "question": response.get("question", "Can you clarify further?")})

@app.route("/results")
def results():
    design = session.get("design", {})
    return render_template("results.html", design=design)