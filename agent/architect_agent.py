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
        model="gpt-5",
        messages=messages,
        temperature=temperature
    )
    return response.choices[0].message.content
    
def clarify_once(conversation):
    """
    Given the chat history, ask the AI for either another clarifying question
    or a signal that it’s ready.
    """
    system_prompt = (
        "You are a senior software architect AI. "
        "You are helping a user clarify their project idea. "
        "If you need more context, respond ONLY as JSON:\n"
        '{"ready": false, "question": "<clarifying question>"}\n'
        "If you are ready to design, respond ONLY as JSON:\n"
        '{"ready": true, "summary": "<short project summary>"}\n'
        "Do not include markdown or extra text."
    )

    messages = [{"role": "system", "content": system_prompt}] + conversation
    raw = ask_llm(messages)

    cleaned = re.sub(r"^```(json)?", "", raw.strip())
    cleaned = re.sub(r"```$", "", cleaned).strip()

    try:
        return json.loads(cleaned)
    except:
        return {"error": raw}

def generate_system_design(conversation):
    """
    Given the clarified conversation, produce the final system design JSON.
    """
    messages = conversation + [
        {"role": "system", "content": (
            "Now that you understand the project, generate a detailed system design JSON "
            "with the following keys: architecture, setup_commands, folder_structure, "
            "mermaid_diagram, recommendations."
        )}
    ]
    raw = ask_llm(messages)
    cleaned = re.sub(r"^```(json)?", "", raw.strip())
    cleaned = re.sub(r"```$", "", cleaned).strip()

    try:
        return json.loads(cleaned)
    except:
        return {"raw_output": raw}