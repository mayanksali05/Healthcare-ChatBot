import os
import venv
import subprocess
import platform

# =========================
# Project Configuration
# =========================

ROOT_DIR = "Healthcare ChatBot"

folders = [
    "backend/routes",
    "backend/rag",
    "backend/ingestion",
    "backend/safety",
    "backend/database/chroma_db",
    "backend/data/raw",
    "backend/data/cleaned",
    "backend/data/chunks",
    "backend/utils",

    "frontend/public",
    "frontend/src/components",
    "frontend/src/pages",
    "frontend/src/services",
    "frontend/src/styles",

    "docs"
]

files = [
    # Backend
    "backend/app.py",
    "backend/config.py",
    "backend/requirements.txt",
    "backend/.env",

    # Routes
    "backend/routes/__init__.py",
    "backend/routes/chat.py",

    # RAG
    "backend/rag/__init__.py",
    "backend/rag/embeddings.py",
    "backend/rag/vector_store.py",
    "backend/rag/retriever.py",
    "backend/rag/generator.py",
    "backend/rag/prompt.py",

    # Ingestion
    "backend/ingestion/__init__.py",
    "backend/ingestion/scraper.py",
    "backend/ingestion/cleaner.py",
    "backend/ingestion/chunker.py",
    "backend/ingestion/metadata.py",

    # Safety
    "backend/safety/__init__.py",
    "backend/safety/filters.py",
    "backend/safety/emergency_detection.py",
    "backend/safety/query_classifier.py",

    # Utils
    "backend/utils/logger.py",
    "backend/utils/helpers.py",

    # Frontend
    "frontend/package.json",
    "frontend/vite.config.js",

    "frontend/src/components/ChatWindow.jsx",
    "frontend/src/components/MessageBubble.jsx",
    "frontend/src/components/SourceCard.jsx",
    "frontend/src/components/SuggestedQuestions.jsx",
    "frontend/src/components/TypingIndicator.jsx",

    "frontend/src/pages/Home.jsx",
    "frontend/src/services/api.js",
    "frontend/src/App.jsx",
    "frontend/src/main.jsx",

    # Docs
    "docs/architecture.md",
    "docs/api_design.md",
    "docs/roadmap.md",

    # Root
    ".gitignore",
    "README.md",
    "docker-compose.yml"
]

# =========================
# Create Project Structure
# =========================

print("\nCreating project structure...\n")

os.makedirs(ROOT_DIR, exist_ok=True)

# Create folders
for folder in folders:
    folder_path = os.path.join(ROOT_DIR, folder)
    os.makedirs(folder_path, exist_ok=True)

# Create files
for file in files:
    file_path = os.path.join(ROOT_DIR, file)

    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    with open(file_path, "w", encoding="utf-8") as f:
        pass

print("✅ Folder structure created")


# =========================
# Create Virtual Environment
# =========================

venv_path = os.path.join(ROOT_DIR, "venv")

print("\nCreating virtual environment...\n")

venv.create(venv_path, with_pip=True)

print("✅ Virtual environment created")


# =========================
# Create .gitignore
# =========================

gitignore_content = """
# Python
venv/
__pycache__/
*.pyc

# Environment
.env

# Node
node_modules/

# Build
dist/

# VSCode
.vscode/

# Mac
.DS_Store

# ChromaDB
backend/database/chroma_db/

# Data
backend/data/raw/
backend/data/cleaned/
backend/data/chunks/
"""

gitignore_path = os.path.join(ROOT_DIR, ".gitignore")

with open(gitignore_path, "w", encoding="utf-8") as f:
    f.write(gitignore_content.strip())

print("✅ .gitignore created")


# =========================
# Initialize Git Repository
# =========================

print("\nInitializing Git repository...\n")

try:
    subprocess.run(
        ["git", "init"],
        cwd=ROOT_DIR,
        check=True
    )
    print("✅ Git repository initialized")

except Exception as e:
    print(f"❌ Git init failed: {e}")


# =========================
# Activation Instructions
# =========================

print("\n==============================")
print("PROJECT SETUP COMPLETE")
print("==============================\n")

system_os = platform.system()

if system_os == "Windows":
    print("Activate virtual environment using:")
    print(rf"{ROOT_DIR}\venv\Scripts\activate")

else:
    print("Activate virtual environment using:")
    print(f"source {ROOT_DIR}/venv/bin/activate")

print("\nNext Steps:")
print("1. Activate venv")
print("2. Install backend dependencies")
print("3. Create React frontend using Vite")
print("4. Start backend development")