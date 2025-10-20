from openai import OpenAI
import json
import re
from dotenv import load_dotenv
import os
load_dotenv()

API_KEY = os.getenv("API_KEY")
client = OpenAI(api_key=API_KEY)

def ask_llm(messages, temperature=0.7):
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        temperature=temperature
    )
    return response.choices[0].message.content

def generate_clarifying_questions(project_description, context=None):
    context = context or {}
    prompt = f"""
You are a software architect AI.
Project: "{project_description}"
Context so far: {json.dumps(context, indent=2)}

Generate 3 clarifying questions to better understand the technical scope.
"""
    return ask_llm([{"role": "user", "content": prompt}])

def generate_system_design(project_description, answers):
    prompt = f"""
You are a senior full-stack architect.
Project description: "{project_description}"
Answers: {json.dumps(answers, indent=2)}

Produce a JSON object with:
["architecture", "setup_commands", "folder_structure", "mermaid_diagram", "recommendations"]
Do not wrap your output in code fences or markdown.
"""
    raw = ask_llm([{"role": "user", "content": prompt}])

    # 🧹 Clean GPT formatting if needed
    cleaned = re.sub(r"^```(json)?", "", raw.strip())
    cleaned = re.sub(r"```$", "", cleaned).strip()

    try:
        data = json.loads(cleaned)
        return data
    except json.JSONDecodeError:
        # Try a relaxed fallback (sometimes it returns nested code blocks)
        try:
            inner_json = re.search(r"\{[\s\S]*\}", cleaned)
            if inner_json:
                return json.loads(inner_json.group(0))
        except:
            pass
        return {"raw_output": raw}