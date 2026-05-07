import subprocess
import sys
import uuid
import os


ALLOWED_IMPORTS = [
    "numpy", "scipy", "sympy", "pandas",
    "matplotlib", "math", "random",
    "itertools", "collections", "statistics"
]

BLOCKED_IMPORTS = [
    "os", "subprocess", "sys", "socket",
    "requests", "pickle", "importlib",
    "shutil", "pathlib"
]


def is_code_safe(code: str) -> tuple[bool, str]:
    for blocked in BLOCKED_IMPORTS:
        if f"import {blocked}" in code or f"from {blocked}" in code:
            return False, f"Blocked import detected: {blocked}"
    return True, "OK"


def run_code(code: str, timeout: int = 30) -> dict:
    safe, reason = is_code_safe(code)
    if not safe:
        return {
            "stdout": "",
            "stderr": reason,
            "error": True,
            "error_type": "SecurityError"
        }

    tmp_file = f"sandbox_tmp_{uuid.uuid4().hex[:8]}.py"

    try:
        with open(tmp_file, "w") as f:
            f.write(code)

        result = subprocess.run(
            [sys.executable, tmp_file],
            capture_output=True,
            text=True,
            timeout=timeout
        )

        return {
            "stdout": result.stdout.strip(),
            "stderr": result.stderr.strip(),
            "error": result.returncode != 0,
            "error_type": None
        }

    except subprocess.TimeoutExpired:
        return {
            "stdout": "",
            "stderr": f"Code timed out after {timeout} seconds",
            "error": True,
            "error_type": "TimeoutError"
        }

    except Exception as e:
        return {
            "stdout": "",
            "stderr": str(e),
            "error": True,
            "error_type": type(e).__name__
        }

    finally:
        if os.path.exists(tmp_file):
            os.remove(tmp_file)