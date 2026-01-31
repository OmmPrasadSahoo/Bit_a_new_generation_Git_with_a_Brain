import typer
import subprocess
import os
import sys
import ast
from rich.console import Console

# --- CONFIGURATION ---
app = typer.Typer(add_completion=False)
console = Console()

# --- HELPER FUNCTIONS ---

def run_git(args, capture=False, check=False):
    """
    Runs git commands with safe encoding for Windows.
    """
    try:
        result = subprocess.run(
            ["git"] + args,
            capture_output=capture,
            text=True,
            check=check,
            encoding="utf-8"  # CRITICAL for Windows to avoid crashes
        )
        return result
    except subprocess.CalledProcessError as e:
        if check:
            raise e
        return e
    except FileNotFoundError:
        console.print("[bold red]Error:[/bold red] Git is not installed.")
        sys.exit(1)

def get_functions_from_code(code):
    """
    Parses Python code and returns a set of function names.
    Used for Level 3: Symbol Awareness.
    """
    try:
        tree = ast.parse(code)
        return {node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)}
    except:
        return set()

# --- LEVEL 1: THE FOUNDATION ---

@app.command(context_settings={"allow_extra_args": True, "ignore_unknown_options": True})
def catch_all(ctx: typer.Context):
    """
    Passes unknown commands (like 'push', 'pull', 'status') directly to Git.
    """
    # If the command is unknown to Bit, let Git handle it
    subprocess.run(["git"] + ctx.args, encoding="utf-8")

@app.command()
def init():
    """
    Smart Init: Initializes git and generates a .gitignore based on project type.
    """
    console.print("[green]Initializing Bit repository...[/green]")
    run_git(["init"], check=True)

    files = os.listdir(".")
    ignore_lines = []

    # Heuristic detection
    if any(f.endswith(".py") for f in files):
        console.print("🐍 Python project detected!")
        ignore_lines += ["__pycache__/", "venv/", ".env"]
    
    if "package.json" in files:
        console.print("📦 Node.js project detected!")
        ignore_lines += ["node_modules/", ".env"]

    if ignore_lines:
        with open(".gitignore", "a", encoding="utf-8") as f:
            f.write("\n".join(ignore_lines) + "\n")
        console.print(f"[bold]✨ Added {len(ignore_lines)} rules to .gitignore[/bold]")

@app.command()
def commit():
    """
    AI Commit: Generates a commit message from staged changes.
    """
    # 1. Get diff
    diff_proc = run_git(["diff", "--cached"], capture=True)
    diff_text = diff_proc.stdout

    if not diff_text:
        console.print("[yellow]Nothing to commit! (Did you run 'git add'?)[/yellow]")
        return

    console.print("[bold cyan]🤖 Bit is analyzing your changes...[/bold cyan]")

    # --- SIMULATED AI RESPONSE ---
    # In production, you would call OpenAI API here
    suggested_message = "feat(core): update logic to handle merge conflicts"
    # -----------------------------
    
    console.print(f"Suggested Message: [bold]{suggested_message}[/bold]")
    
    if typer.confirm("Do you want to use this message?"):
        run_git(["commit", "-m", suggested_message])
        console.print("[green]✔ Committed successfully![/green]")
    else:
        console.print("[red]Commit aborted.[/red]")

# --- LEVEL 2: THE ARCHITECT (Technical Depth) ---

@app.command()
def ghost(name: str):
    """
    Ghost Branch: Creates a hidden branch reference that doesn't clutter 'git branch'.
    """
    try:
        # Get current commit SHA
        sha = subprocess.check_output(["git", "rev-parse", "HEAD"], encoding="utf-8").strip()
        
        # Create custom ref
        ghost_ref = f"refs/bit/ghosts/{name}"
        run_git(["update-ref", ghost_ref, sha], check=True)
        
        console.print(f"[bold purple]👻 Ghost branch '{name}' created![/bold purple]")
        console.print(f"Stored securely at: {ghost_ref}")
    except:
        console.print("[red]Error: You need at least one commit to create a ghost branch.[/red]")

@app.command()
def merge(branch: str, preview: bool = False):
    """
    Bit Merge:
    --preview: Uses 'git merge-tree' to predict conflicts in memory without touching files.
    """
    if not preview:
        run_git(["merge", branch])
        return

    console.print(f"[bold cyan]🔮 Gazing into the future of merging '{branch}'...[/bold cyan]")
    
    try:
        # git merge-tree HEAD <target> performs an in-memory merge
        result = run_git(["merge-tree", "HEAD", branch], capture=True)
        output = result.stdout
        
        # Check output for conflict markers
        if "conflict" in output.lower() or "<<<<<<<" in output:
            console.print(f"[bold red]💥 DANGER: Conflict detected![/bold red]")
            console.print("If you merge now, your files will break.")
            console.print("Bit prevented this headache. You're welcome.")
        else:
            console.print(f"[bold green]✅ Safe to merge! No conflicts detected.[/bold green]")
            
    except Exception as e:
        console.print(f"[red]Error checking merge: {e}[/red]")

# --- LEVEL 3: THE VISIONARY (Symbol Awareness) ---

@app.command()
def analyze():
    """
    Symbol Awareness: Detects EXACTLY which Python functions changed.
    """
    console.print("[bold purple]🧠 Analyzing Code Symbols...[/bold purple]")
    
    # Get modified files from git status
    status_proc = run_git(["status", "--porcelain"], capture=True)
    modified_files = []
    
    for line in status_proc.stdout.splitlines():
        # Check for Modified (M) Python files
        if line.strip().endswith(".py") and "M" in line:
            modified_files.append(line.split()[-1])

    if not modified_files:
        console.print("No modified Python files found.")
        return

    for filename in modified_files:
        try:
            console.print(f"\n📂 Scanning [bold]{filename}[/bold]...")

            # 1. Read current file content
            with open(filename, "r", encoding="utf-8") as f:
                current_code = f.read()
            
            # 2. Read old file content from HEAD
            old_code_proc = run_git(["show", f"HEAD:{filename}"], capture=True)
            old_code = old_code_proc.stdout

            # 3. Compare symbols
            current_funcs = get_functions_from_code(current_code)
            old_funcs = get_functions_from_code(old_code)
            
            # Simple diff of sets
            new_funcs = current_funcs - old_funcs
            
            if new_funcs:
                console.print(f"   [green]+ New Functions: {', '.join(new_funcs)}[/green]")
            
            # In a real "Hot Zone" implementation, you would check a database here
            console.print(f"   [yellow]⚠  Activity detected in {len(current_funcs)} functions.[/yellow]")

        except Exception as e:
            console.print(f"[red]Skipping {filename}: {e}[/red]")

if __name__ == "__main__":
    app()
    Print("Omm")