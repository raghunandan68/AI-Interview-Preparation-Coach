import requests
import subprocess
import sys
import tempfile
import os

# Piston API endpoint - Official public instance discontinued Feb 2026.
# Users can provide their own instance URL in .env as PISTON_INSTANCE_URL
PISTON_API_URL = os.getenv("PISTON_INSTANCE_URL", "https://emkc.org/api/v2/piston/execute")

# Map of common languages to Piston runtime identifiers
LANGUAGE_MAP = {
    "python": {"language": "python", "version": "3.10.0"},
    "javascript": {"language": "javascript", "version": "18.15.0"},
    "c_cpp": {"language": "c++", "version": "10.2.0"},
    "java": {"language": "java", "version": "15.0.2"},
    "csharp": {"language": "csharp", "version": "6.12.0"},
    "c": {"language": "c", "version": "10.2.0"}
}

def execute_code(language, code):
    """
    Executes code. Uses local execution for Python as a fallback 
    since public Piston API is often discontinued or restricted.
    """
    if language == "python":
        return execute_python_locally(code)
    
    # Try Piston API
    lang_info = LANGUAGE_MAP.get(language)
    if not lang_info:
        return {"error": f"Unsupported language: {language}"}

    payload = {
        "language": lang_info["language"],
        "version": lang_info["version"],
        "files": [{"content": code}]
    }

    try:
        response = requests.post(PISTON_API_URL, json=payload, timeout=10)
        
        if response.status_code == 401 or response.status_code == 403 or response.status_code == 404:
            return {"error": (
                f"The code execution service (Piston) for '{language}' returned {response.status_code}. "
                "The official public Piston API was DISCONTINUED in Feb 2026. "
                "To fix this, you can: \n"
                "1. Host your own Piston instance and set PISTON_INSTANCE_URL in .env\n"
                "2. Use a different language (Python is support locally out-of-the-box)\n"
                "3. Configure a private Piston instance URL if you have one."
            )}
        
        response.raise_for_status()
        result = response.json()
        
        run_res = result.get("run", {})
        return {
            "stdout": run_res.get("stdout", ""),
            "stderr": run_res.get("stderr", ""),
            "output": run_res.get("output", ""),
            "code": run_res.get("code", 0)
        }
    except Exception as e:
        return {"error": f"API Error: {str(e)}. Local execution is currently only supported for Python."}

def execute_python_locally(code):
    """
    Runs Python code in a subprocess.
    """
    try:
        with tempfile.NamedTemporaryFile(suffix=".py", delete=False, mode='w', encoding='utf-8') as f:
            f.write(code)
            temp_path = f.name
        
        # Run the script with empty input to prevent hanging on input()
        result = subprocess.run(
            [sys.executable, temp_path],
            input="", # Provide empty string to stdin
            capture_output=True,
            text=True,
            timeout=15
        )
        
        # Cleanup
        os.unlink(temp_path)
        
        return {
            "stdout": result.stdout,
            "stderr": result.stderr,
            "output": result.stdout + result.stderr,
            "code": result.returncode
        }
    except subprocess.TimeoutExpired:
        if os.path.exists(temp_path):
            os.unlink(temp_path)
        return {"error": "Execution timed out (15s limit). Please check for infinite loops or very slow logic."}
    except Exception as e:
        if os.path.exists(temp_path):
            os.unlink(temp_path)
        return {"error": f"Local execution error: {str(e)}"}
