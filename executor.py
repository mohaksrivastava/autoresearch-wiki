import subprocess
import os

def ensure_dir(path):
    os.makedirs(path, exist_ok=True)

def execute_python_code(code: str, workspace_dir="workspace"):
    """
    Writes the Python code to a file in the workspace directory and executes it.
    Returns a tuple (stdout, stderr, return_code).
    """
    ensure_dir(workspace_dir)
    script_path = os.path.join(workspace_dir, "temp_script.py")

    with open(script_path, "w", encoding="utf-8") as f:
        f.write(code)

    try:
        result = subprocess.run(
            ["python", script_path],
            capture_output=True,
            text=True,
            timeout=60 # Prevent infinite loops
        )
        return result.stdout, result.stderr, result.returncode
    except subprocess.TimeoutExpired:
        return "", "Execution timed out after 60 seconds.", -1
    except Exception as e:
        return "", str(e), -1
