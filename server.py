# server.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import subprocess
import ast
import os
import hashlib

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- MODELS ---
class GhostRequest(BaseModel):
    name: str

class FileWriteRequest(BaseModel):
    filename: str
    content: str

class RunRequest(BaseModel):
    filename: str

# --- HELPERS ---
def run_command(args):
    try:
        # encoding='utf-8' is safe for Windows
        result = subprocess.run(args, capture_output=True, text=True, encoding="utf-8")
        return result.stdout.strip()
    except Exception as e:
        return ""

def get_function_hashes(code):
    """
    Returns a dict {func_name: hash_of_body}
    This prevents false positives by checking if code ACTUALLY changed.
    """
    try:
        tree = ast.parse(code)
        funcs = {}
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # Hash the structure of the function
                dump = ast.dump(node)
                funcs[node.name] = hashlib.md5(dump.encode()).hexdigest()
        return funcs
    except:
        return {}

# --- FILE OPERATIONS ---

@app.get("/api/file")
def read_file(filename: str):
    try:
        if not os.path.exists(filename):
             return {"content": ""} # Handle new files
        with open(filename, "r", encoding="utf-8") as f:
            return {"content": f.read()}
    except Exception as e:
        return {"content": f"Error: {str(e)}"}

@app.post("/api/save")
def save_file(req: FileWriteRequest):
    try:
        # This handles creating NEW files too
        with open(req.filename, "w", encoding="utf-8") as f:
            f.write(req.content)
        return {"success": True, "log": f"Saved {req.filename}"}
    except Exception as e:
        return {"success": False, "log": str(e)}

@app.post("/api/run")
def run_script(req: RunRequest):
    try:
        # 1. Check if file exists
        if not os.path.exists(req.filename):
            return {"success": False, "output": f"File '{req.filename}' not found on disk. Save it first!"}

        # 2. Run with captured Output AND Errors
        result = subprocess.run(
            ["python", req.filename], 
            capture_output=True, 
            text=True, 
            encoding="utf-8", 
            timeout=10 # Increased timeout
        )
        
        # Combine Output (stdout) and Errors (stderr)
        output = result.stdout
        if result.stderr:
            output += "\n[ERROR]:\n" + result.stderr
            
        return {"success": True, "output": output if output.strip() else "[Process finished with no output]"}
    except Exception as e:
        return {"success": False, "output": f"Execution Failed: {str(e)}"}

# --- GIT INTELLIGENCE ---

@app.get("/api/status")
def get_status():
    output = run_command(["git", "status", "--porcelain"])
    files = []
    if output:
        for line in output.splitlines():
            parts = line.strip().split()
            if len(parts) >= 2:
                files.append({"status": parts[0], "file": parts[-1]})
    
    # List all python files (even those not modified)
    all_files = [f for f in os.listdir(".") if f.endswith(".py")]
    return {"files": files, "all_files": all_files}

@app.get("/api/diff")
def get_diff(file: str):
    return {"diff": run_command(["git", "diff", "HEAD", file])}

@app.get("/api/symbols")
def get_symbols():
    """
    Level 3 Fix: Only report function if the Body Hash changed.
    """
    status_output = run_command(["git", "status", "--porcelain"])
    modified_functions = []

    for line in status_output.splitlines():
        if line.strip().endswith(".py") and "M" in line:
            filename = line.split()[-1]
            try:
                # 1. Get Current Code
                with open(filename, "r", encoding="utf-8") as f: 
                    current_code = f.read()
                
                # 2. Get Old Code (HEAD)
                old_code = run_command(["git", "show", f"HEAD:{filename}"])
                
                # 3. Compare Hashes
                curr_hashes = get_function_hashes(current_code)
                old_hashes = get_function_hashes(old_code)
                
                # Check intersection of names, but difference in hashes
                common_names = set(curr_hashes.keys()).intersection(set(old_hashes.keys()))
                
                for name in common_names:
                    if curr_hashes[name] != old_hashes[name]:
                        modified_functions.append(f"{filename} :: {name}()")
                        
            except Exception as e: 
                continue

    return {"functions": modified_functions}

@app.get("/api/ghosts")
def get_ghosts():
    output = run_command(["git", "show-ref"])
    ghosts = [line.split("/")[-1] for line in output.splitlines() if "refs/bit/ghosts/" in line]
    return {"ghosts": ghosts}

@app.post("/api/ghosts")
def create_ghost(req: GhostRequest):
    sha = run_command(["git", "rev-parse", "HEAD"])
    if not sha: return {"success": False, "log": "No commits yet."}
    run_command(["git", "update-ref", f"refs/bit/ghosts/{req.name}", sha])
    return {"success": True, "log": f"👻 Spawned ghost '{req.name}'"}

@app.get("/api/history")
def get_history():
    # FIXED: Use '|||' as separator to avoid splitting commit messages
    # %h = hash, %s = subject, %an = author name, %ar = relative date
    output = run_command(["git", "log", "-n", "10", "--pretty=format:%h|||%s|||%an|||%ar"])
    commits = []
    if output:
        for line in output.splitlines():
            parts = line.split("|||")
            if len(parts) >= 4:
                commits.append({
                    "hash": parts[0], 
                    "msg": parts[1], 
                    "author": parts[2], 
                    "date": parts[3]
                })
    return {"commits": commits}

@app.post("/api/commit")
def ai_commit():
    run_command(["git", "add", "."])
    # Simulating AI behavior
    run_command(["git", "commit", "-m", "feat(auto): AI system logic update"])
    return {"success": True, "log": "🤖 AI Auto-Commit Execution Complete."}