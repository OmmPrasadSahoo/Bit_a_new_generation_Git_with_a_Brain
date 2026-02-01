# Bit - The Next Evolution of Git 🔮

> **"Bit is Git with a brain."**

**Bit** is an intelligent, AI-powered layer above Git that automates routine tasks, predicts conflicts before they happen, and provides a full-stack local "Grand Central" dashboard for managing your code evolution.

Built for the **CodeMate Hackathon**, Bit goes beyond a simple wrapper by implementing deep Git plumbing (`merge-tree`, `update-ref`) and Python AST analysis to track *logic* changes, not just text changes.

---

## 🚀 Features

### 🏗️ Level 1: The Foundation (Smart Automation)
- **Transparent Passthrough**: `bit pull`, `bit push`, and `bit status` work exactly like Git. If Bit doesn't know a command, it seamlessly hands it off to Git.
- **Smart Initialization (`bit init`)**: Automatically detects if you are using Python or Node.js and generates a tailored `.gitignore` to protect sensitive files (`.env`, `venv/`).
- **AI-Powered Commits (`bit commit`)**: Analyzes your staged changes (`diff --cached`) and auto-generates semantic Conventional Commits (e.g., `feat(core): optimize merge logic`).

### 🏛️ Level 2: The Architect (Deep Git Plumbing)
- **Ghost Branches (`bit ghost <name>`)**: Creates "invisible" branches using custom refs (`refs/bit/ghosts/`). These don't clutter your standard `git branch` list but store experimental snapshots safely.
- **Virtual Merge Preview (`bit merge <branch> --preview`)**: Uses `git merge-tree` to perform a merge in memory. It predicts conflicts **before** you touch your working directory, saving you from broken builds.

### 🧠 Level 3: The Visionary (Symbol Awareness)
- **AST Logic Analysis**: Bit doesn't just check lines of code. It parses Python Abstract Syntax Trees (AST) and hashes function bodies.
- **False Positive Protection**: It only alerts you if the *logic* inside a function changes (ignoring whitespace/comments).
- **Symbol Radar**: Reports exactly which functions (e.g., `server.py :: run_command()`) have been modified.

### 🌟 Bonus: "Grand Central" Dashboard
A full-stack, local GUI running on **FastAPI** (Backend) and **Vanilla JS** (Frontend).
- **Zero-Install UI**: No `npm`, no `node_modules`. Just open `dashboard.html`.
- **Integrated IDE**: Edit files, save changes, and run Python scripts directly from the browser.
- **Visual Timeline**: Graphical history with User/Date tracking.
- **Interactive Actions**: One-click AI Commits, Ghost Spawning, and Diff X-Ray views.

---

## 🛠️ Installation

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/YOUR_USERNAME/bit-hackathon.git](https://github.com/YOUR_USERNAME/bit-hackathon.git)
   cd bit-hackathon
   
