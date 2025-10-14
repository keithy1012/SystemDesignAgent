import os 
import subprocess
from openai import OpenAI
import json

API_KEY = os.getenv("API_KEY")
TEMPERATURE = 0.5
client = OpenAI(api_key = API_KEY)

def ask_llm(messages):
    response = client.chat.completions.create(
        model="gpt-5-mini",
        messages=messages,
        temperature=TEMPERATURE
    )
    return response.choices[0].message["content"]

def generate_clarifying_questions(project_desc, context):
    prompt = f"""
    You are a software architect AI.
    Project: "{project_desc}"
    Context so far: {json.dumps(context, indent=2)}

    Generate 5 clarifying questions to better understand the technical scope.
    """
    return ask_llm([{"role": "user", "content": prompt}])

def generate_system_design(project_description, answers):
    prompt = f"""
    You are a senior full-stack architect.
    Project description: "{project_description}"
    Answers: {json.dumps(answers, indent=2)}

    Produce:
    1. High-level system architecture (frontend, backend, databases, cloud)
    2. Detailed setup commands (npm, npx, docker, AWS CLI, etc.)
    3. Recommended folder structure
    4. Mermaid diagram (use code block syntax)
    5. Optional dependencies or integrations (auth, caching, CI/CD)
    Return as JSON with keys:
    ["architecture", "setup_commands", "folder_structure", "mermaid_diagram", "recommendations"]
    """
    raw = ask_llm([{"role": "user", "content": prompt}])
    try:
        return json.loads(raw)
    except:
        # fallback if GPT output is not strict JSON
        return {"raw_output": raw}
    
# Generate the project
def execute_setup_commands(commands):
    print("\n Running setup commands...")
    for cmd in commands.split("\n"):
        cmd = cmd.strip()
        if not cmd or cmd.startswith("#"):
            continue
        print(f"\n> {cmd}")
        try:
            subprocess.run(cmd, shell=True, check=True)
        except subprocess.CalledProcessError:
            print(f" Command failed: {cmd}")

# Creates the base template for a project
def create_folder_structure(structure, base_path="."):
    """
    Creates folders and files based on GPT's suggested structure.
    """
    print("\n Creating project structure...")
    for path in structure.split("\n"):
        path = path.strip()
        if not path:
            continue
        if path.endswith("/"):
            os.makedirs(os.path.join(base_path, path), exist_ok=True)
        else:
            full_path = os.path.join(base_path, path)
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            with open(full_path, "w") as f:
                f.write("// Auto-generated placeholder\n")

def save_design_docs(design):
    os.makedirs("project_docs", exist_ok=True)
    with open("project_docs/system_design.json", "w") as f:
        json.dump(design, f, indent=2)
    with open("project_docs/system_architecture.mmd", "w") as f:
        f.write(design.get("mermaid_diagram", ""))
    print("\nSaved design files in ./project_docs")


def interactive_agent():
    print("=== AI PROJECT ARCHITECT ===\n")
    project_description = input("Describe your project: ")

    context = {}
    for i in range(5):
        questions = generate_clarifying_questions(project_description, context)
        print(f"\nClarifying Questions (Round {i+1}):\n{questions}")
        answers = input("\nYour answers (plain text or JSON): ")
        try:
            answers_dict = json.loads(answers)
        except:
            answers_dict = {"answers": answers}
        context.update(answers_dict)

        more = input("\nAsk more clarifying questions? (y/n): ")
        if more.lower() != "y":
            break

    design = generate_system_design(project_description, context)
    print("\n=== SYSTEM DESIGN GENERATED ===")
    print(json.dumps(design, indent=2) if isinstance(design, dict) else design)

    # Create local project folder
    base_dir = input("\nEnter base folder name for project (default: ./project): ") or "project"
    os.makedirs(base_dir, exist_ok=True)

    # Create structure + setup commands
    if "folder_structure" in design:
        create_folder_structure(design["folder_structure"], base_path=base_dir)
    if "setup_commands" in design:
        execute_setup_commands(design["setup_commands"])
    save_design_docs(design)

    print("\nAll done! Your project skeleton and design files are ready.")

if __name__ == "__main__":
    interactive_agent()