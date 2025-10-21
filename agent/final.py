#!/usr/bin/env python3
"""
AI Project Architect v3
- Interactive LLM-driven clarifying questions + system design
- Auto-generate folder structure
- Auto-generate Dockerfile(s), docker-compose.yml, and .env.template
NOTE: Replace OpenAI client code with your SDK of choice / credentials.
"""

import os
import json
import subprocess
from typing import Dict, Any, List

# --------- Replace this with your OpenAI client call (example placeholder) ----------
# For the sample, we will mock ask_llm responses unless you wire your API.
# If using OpenAI SDK, replace `ask_llm` with your API call.
def ask_llm(messages, temperature=0.7):
    # Placeholder for LLM call.
    # Replace with appropriate call to GPT-5 or your LLM endpoint.
    # For now, raise to remind you to plug in your API.
    raise RuntimeError("Please replace ask_llm() with your LLM API call (OpenAI/gpt-5).")

# ---------------- LLM Helpers ----------------
def generate_clarifying_questions(project_description: str, context: Dict[str, Any]) -> str:
    prompt = f"""
You are a software architect AI.
Project: "{project_description}"
Context so far: {json.dumps(context, indent=2)}
Generate 3 clarifying questions to better understand technical scope.
"""
    return ask_llm([{"role": "user", "content": prompt}])

def generate_system_design(project_description: str, answers: Dict[str, Any]) -> Dict[str, Any]:
    prompt = f"""
You are a senior full-stack architect.
Project description: "{project_description}"
Answers: {json.dumps(answers, indent=2)}

Produce JSON with keys:
- architecture: short textual description
- services: mapping of service_name -> {{"type": "react|node|python|static", "port": <int>, "path": "<relative path>"}}
- databases: list e.g. ["postgres","redis"]
- setup_commands: newline-separated commands to initialize repo
- folder_structure: newline-separated list of files/folders to create
- mermaid_diagram: optional mermaid code block
- recommendations: additional notes

Return valid JSON only.
"""
    raw = ask_llm([{"role": "user", "content": prompt}])
    try:
        return json.loads(raw)
    except Exception as e:
        # If the LLM does not return strict JSON, return a fallback wrapper
        return {"raw_output": raw}

# ---------------- File generation helpers ----------------
def write_file(path: str, content: str):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)

def create_folder_structure(structure_text: str, base_path: str):
    for line in structure_text.splitlines():
        line = line.strip()
        if not line:
            continue
        full = os.path.join(base_path, line)
        if line.endswith("/"):
            os.makedirs(full, exist_ok=True)
        else:
            os.makedirs(os.path.dirname(full), exist_ok=True)
            if not os.path.exists(full):
                write_file(full, "// placeholder\n")

# ---------------- Dockerfile templates ----------------
def dockerfile_for_node(service_name: str) -> str:
    return f"""# Dockerfile for {service_name} (Node)
FROM node:18-alpine AS deps
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production

FROM node:18-alpine AS runner
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .
ENV NODE_ENV=production
EXPOSE 3000
CMD ["node", "index.js"]
"""

def dockerfile_for_react(service_name: str) -> str:
    return f"""# Multi-stage Dockerfile for {service_name} (React)
FROM node:18-alpine as build
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM nginx:stable-alpine as runtime
COPY --from=build /app/build /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
"""

def dockerfile_for_python(service_name: str) -> str:
    return f"""# Dockerfile for {service_name} (Python)
FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
"""

# ---------------- docker-compose generation ----------------
def generate_docker_compose(design: Dict[str, Any]) -> str:
    services = design.get("services", {})
    dbs = design.get("databases", [])
    compose = {
        "version": "3.8",
        "services": {}
    }
    # Add app services
    for name, svc in services.items():
        svc_type = svc.get("type", "").lower()
        port = svc.get("port")
        path = svc.get("path", name)
        service_entry = {
            "build": {"context": f"./{path}"},
            "volumes": [f"./{path}:/app"],
            "ports": [f"{port}:{port}"] if port else [],
            "environment": [
                "NODE_ENV=development" if svc_type in ("node","react") else ""
            ],
            "depends_on": []
        }
        # trim empty elements
        service_entry = {k: v for k, v in service_entry.items() if v and v != [""]}
        compose["services"][name] = service_entry

    # Databases
    if "postgres" in [d.lower() for d in dbs]:
        compose["services"]["postgres"] = {
            "image": "postgres:15",
            "restart": "unless-stopped",
            "environment": {
                "POSTGRES_USER": "postgres",
                "POSTGRES_PASSWORD": "${POSTGRES_PASSWORD:-postgres}",
                "POSTGRES_DB": "${POSTGRES_DB:-app_db}"
            },
            "volumes": ["postgres_data:/var/lib/postgresql/data"],
            "ports": ["5432:5432"]
        }
        # make app services depend on postgres
        for svc_name in compose["services"]:
            if svc_name not in ("postgres","redis"):
                compose["services"][svc_name].setdefault("depends_on", []).append("postgres")

    if "redis" in [d.lower() for d in dbs]:
        compose["services"]["redis"] = {
            "image": "redis:7-alpine",
            "ports": ["6379:6379"],
            "volumes": ["redis_data:/data"]
        }
        for svc_name in compose["services"]:
            if svc_name not in ("postgres","redis"):
                compose["services"][svc_name].setdefault("depends_on", []).append("redis")

    # Volumes
    volumes = {}
    if any(k == "postgres" for k in compose["services"]):
        volumes["postgres_data"] = None
    if any(k == "redis" for k in compose["services"]):
        volumes["redis_data"] = None

    # Render compose YAML manually to keep dependency-free
    lines = []
    lines.append("version: '3.8'")
    lines.append("services:")
    for svc_name, svc in compose["services"].items():
        lines.append(f"  {svc_name}:")
        for k, v in svc.items():
            if isinstance(v, dict):
                lines.append(f"    {k}:")
                for kk, vv in v.items():
                    lines.append(f"      {kk}: {json.dumps(vv)}")
            elif isinstance(v, list):
                lines.append(f"    {k}:")
                for item in v:
                    lines.append(f"      - {item}")
            elif isinstance(v, str):
                lines.append(f"    {k}: {v}")
            else:
                # fallback
                lines.append(f"    {k}: {json.dumps(v)}")
    if volumes:
        lines.append("volumes:")
        for vol in volumes:
            lines.append(f"  {vol}:")
            lines.append("    driver: local")
    return "\n".join(lines)

# ---------------- .env template ----------------
def generate_env_template(design: Dict[str, Any]) -> str:
    lines = []
    # DB
    if "postgres" in [d.lower() for d in design.get("databases", [])]:
        lines += [
            "POSTGRES_USER=postgres",
            "POSTGRES_PASSWORD=postgres",
            "POSTGRES_DB=app_db",
            "DATABASE_URL=postgresql://postgres:postgres@postgres:5432/app_db"
        ]
    if "redis" in [d.lower() for d in design.get("databases", [])]:
        lines.append("REDIS_URL=redis://redis:6379/0")
    # Example cloud keys
    lines += [
        "AWS_REGION=us-east-1",
        "AWS_S3_BUCKET=my-app-bucket",
        "AWS_ACCESS_KEY_ID=REPLACE_ME",
        "AWS_SECRET_ACCESS_KEY=REPLACE_ME",
        ""
    ]
    return "\n".join(lines)

# ---------------- Main orchestration ----------------
def scaffold_from_design(design: Dict[str, Any], base_dir: str):
    # Create base_dir
    os.makedirs(base_dir, exist_ok=True)

    # Folder structure
    folder_structure = design.get("folder_structure")
    if folder_structure:
        create_folder_structure(folder_structure, base_path=base_dir)
    else:
        # default structure from services
        services = design.get("services", {})
        for name, svc in services.items():
            path = svc.get("path", name)
            create_folder_structure(f"{path}/\n{path}/README.md", base_path=base_dir)

    # Generate Dockerfiles for services
    services = design.get("services", {})
    for name, svc in services.items():
        svc_type = svc.get("type", "").lower()
        path = os.path.join(base_dir, svc.get("path", name))
        if svc_type == "node":
            content = dockerfile_for_node(name)
        elif svc_type == "react":
            content = dockerfile_for_react(name)
        elif svc_type == "python":
            content = dockerfile_for_python(name)
        else:
            # generic placeholder Dockerfile
            content = f"# Dockerfile for {name}\nFROM alpine\nCMD [\"/bin/sh\"]\n"
        write_file(os.path.join(path, "Dockerfile"), content)
        # Add minimal entrypoint placeholders
        if svc_type == "node":
            # placeholder index.js and package.json if absent
            idx = os.path.join(path, "index.js")
            pkg = os.path.join(path, "package.json")
            if not os.path.exists(idx):
                write_file(idx, "console.log('Hello from Node service');\n")
            if not os.path.exists(pkg):
                write_file(pkg, json.dumps({"name": name, "version": "0.1.0", "main": "index.js", "scripts": {"start": "node index.js"}}, indent=2))
        if svc_type == "python":
            req = os.path.join(path, "requirements.txt")
            main_py = os.path.join(path, "main.py")
            if not os.path.exists(req):
                write_file(req, "fastapi\nuvicorn\n")
            if not os.path.exists(main_py):
                write_file(main_py, "from fastapi import FastAPI\napp = FastAPI()\n\n@app.get('/')\ndef root():\n    return {'hello':'world'}\n")

    # Generate docker-compose.yml
    compose_text = generate_docker_compose(design)
    write_file(os.path.join(base_dir, "docker-compose.yml"), compose_text)

    # Generate .env template
    env_text = generate_env_template(design)
    write_file(os.path.join(base_dir, ".env.template"), env_text)

    # Save design json + mermaid if present
    write_file(os.path.join(base_dir, "project_design.json"), json.dumps(design, indent=2))
    mermaid = design.get("mermaid_diagram", "")
    if mermaid:
        write_file(os.path.join(base_dir, "architecture.mmd"), mermaid)

    print(f"\nScaffolded project at: {base_dir}")
    print("Files generated:")
    for root, dirs, files in os.walk(base_dir):
        for f in files:
            print(" -", os.path.join(root, f))

# ---------------- Safe command execution ----------------
def execute_setup_commands(commands: str, cwd: str = "."):
    """
    Very conservative: prints commands, then attempts to run simple safe ones.
    Avoids destructive commands. You can inspect commands before running.
    """
    if not commands:
        return
    print("\nSetup commands the agent recommends:")
    for line in commands.splitlines():
        line = line.strip()
        if not line:
            continue
        print("  ", line)

    run = input("\nRun these commands now? (y/N): ")
    if run.lower() != "y":
        print("Skipping execution of setup commands.")
        return

    for line in commands.splitlines():
        cmd = line.strip()
        if not cmd:
            continue
        # disallow obviously destructive commands
        blocked = ["rm -rf", "sudo", "dd ", ":(){:", "mkfs", ">:"]  # simple blacklist
        if any(x in cmd for x in blocked):
            print(f"Skipping potentially dangerous command: {cmd}")
            continue
        try:
            subprocess.run(cmd, shell=True, check=True, cwd=cwd)
        except subprocess.CalledProcessError as e:
            print(f"Command failed: {cmd}\n  {e}")

# ---------------- Interactive CLI ----------------
def interactive_agent():
    print("=== AI Project Architect v3 ===")
    project_description = input("Describe your project idea: ").strip()
    context = {}

    # Ask up to 3 clarifying rounds
    for i in range(3):
        try:
            questions = generate_clarifying_questions(project_description, context)
        except Exception as e:
            print("\n(LLM not wired) Example clarifying questions:")
            questions = "1) Who is the primary user?\n2) Expected scale? (100 users vs 1M)\n3) Preferred language/stack?"
        print(f"\nClarifying Questions (Round {i+1}):\n{questions}")
        answers = input("\nYour answers (plain text or JSON): ")
        try:
            answers_dict = json.loads(answers)
        except:
            answers_dict = {"answers_round_"+str(i+1): answers}
        context.update(answers_dict)
        more = input("\nAsk more clarifying questions? (y/N): ")
        if more.lower() != "y":
            break

    # Generate system design (LLM)
    try:
        design = generate_system_design(project_description, context)
    except Exception as e:
        print("\n(LLM not wired) Creating example design fallback.")
        design = {
            "architecture": "React frontend, Node backend, Postgres, Redis",
            "services": {
                "client": {"type": "react", "port": 80, "path": "client"},
                "server": {"type": "node", "port": 3000, "path": "server"},
                "ai_service": {"type": "python", "port": 8000, "path": "ai_service"}
            },
            "databases": ["postgres", "redis"],
            "setup_commands": "npx create-react-app client\nmkdir server && cd server && npm init -y && npm install express\nmkdir ai_service && cd ai_service && python -m venv venv",
            "folder_structure": "client/\nserver/\nai_service/\nservices/\nREADME.md\ndocker-compose.yml",
            "mermaid_diagram": "graph LR\n client --> server\n server --> postgres\n server --> redis",
            "recommendations": "Add CI with GitHub Actions; use S3 for file storage"
        }

    # Show the design summary
    print("\n=== SYSTEM DESIGN SUMMARY ===")
    print(json.dumps(design, indent=2))

    base_dir = input("\nEnter local base folder to scaffold (default './project'): ").strip() or "project"
    scaffold_from_design(design, base_dir)

    # Optionally run setup commands
    setup_cmds = design.get("setup_commands", "")
    if setup_cmds:
        execute_setup_commands(setup_cmds, cwd=base_dir)

    print("\nDone. Inspect the generated files and tweak them as needed.")

if __name__ == "__main__":
    interactive_agent()
