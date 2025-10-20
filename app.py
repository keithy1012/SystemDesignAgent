from flask import Flask, render_template, request, redirect, url_for, session
from architect_agent import generate_clarifying_questions, generate_system_design
import json
import os
from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        project_desc = request.form["project_desc"]
        session["project_desc"] = project_desc
        questions = generate_clarifying_questions(project_desc)
        session["questions"] = questions
        return redirect(url_for("questions"))
    return render_template("index.html")

@app.route("/questions", methods=["GET", "POST"])
def questions():
    questions = session.get("questions")
    if request.method == "POST":
        answers = request.form["answers"]
        session["answers"] = answers
        return redirect(url_for("results"))
    return render_template("questions.html", questions=questions)

@app.route("/results")
def results():
    project_desc = session.get("project_desc")
    answers = session.get("answers")
    design = generate_system_design(project_desc, {"answers": answers})
    print(json.dumps(design, indent=2)) 
    return render_template("results.html", design=design)

if __name__ == "__main__":
    app.run(debug=True)
