# System Design Agent Flask Application

A lightweight Flask web application that generates system design blueprints for project ideas using an intelligent AI agent. The application accepts a user's project description and answers to several questions, then produces a detailed system architecture, setup instructions, folder structure, and recommendations, all visualized with Mermaid diagrams.

---

## Features

- **AI-Powered System Design** — Automatically generates backend, frontend, database, and cloud architecture specifications.
- **Dynamic Setup Commands** — Provides shell commands for initializing project structure and dependencies.
- **Folder Structure Generator** — Suggests best-practice directory layouts for both backend and frontend components.
- **Mermaid Diagram Visualization** — Displays clear architecture diagrams illustrating component connections.
- **Simple Flask Frontend** — Collects project input via web form and displays structured results.

---

## Technology Stack

| Layer         | Technology                                 |
| ------------- | ------------------------------------------ |
| Backend       | Flask (Python)                             |
| Frontend      | HTML + Bootstrap                           |
| AI Logic      | Python Agent with system design generation |
| Visualization | Mermaid.js                                 |
| Data Handling | Flask Session                              |

---

## Project Structure

```
system-design-agent/
├── app.py
├── templates/
│   ├── index.html
│   └── results.html
├── static/
│   └── style.css
├── agent/
│   ├── __init__.py
│   └── design_agent.py
├── requirements.txt
└── README.md
```

---

## Setup and Local Deployment

### Step 1: Clone the Repository

```bash
git clone https://github.com/your-username/system-design-agent.git
cd system-design-agent
```

### Step 2: Create a Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate  # Mac/Linux
venv\Scripts\activate     # Windows
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Run the Flask Server

```bash
flask run
```

The application will be available at http://127.0.0.1:5000

---

## Usage

1. Open the application in your browser.
2. Enter your project description (e.g., "A Twitter clone with scalable backend and live notifications").
3. Answer the optional questions.
4. Click "Generate Design".
5. View the complete architecture output including:
   - Technology stack suggestions
   - Setup commands
   - Folder structure
   - Mermaid diagram
   - Best practice recommendations

---

## Architecture Overview

The application operates through the following workflow:

1. The user submits a project description via the homepage form.
2. Flask stores the input in session variables.
3. The `/results` route invokes the `generate_system_design()` agent function.
4. The agent generates architecture details, setup commands, folder structure, Mermaid diagram, and best practices.
5. Flask renders all results in `results.html` dynamically.

---

## Dependencies

- Flask
- openai (if using API-based agent)
- Markdown
- python-dotenv (for environment variables)
- Mermaid (JavaScript embedded in HTML)

Install all dependencies with:

```bash
pip install flask openai markdown python-dotenv
```

---

## Environment Variables

Create a `.env` file in the root directory:

```
OPENAI_API_KEY=your_api_key_here
FLASK_SECRET_KEY=your_secret_key
```

---

## Author

Keith Yao  
Computer Science, Northeastern University  
Aspiring Machine Learning and AI Engineer
