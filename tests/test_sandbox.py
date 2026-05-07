from sandbox.executor import run_code, is_code_safe


def test_simple_code_runs():
    code = "print(2 + 2)"
    result = run_code(code)
    assert result["stdout"] == "4"
    assert result["error"] == False
    print("✅ Simple code test passed")


def test_numpy_works():
    code = """
import numpy as np
matrix = np.array([[1,2],[3,4]])
print(np.linalg.det(matrix))
"""
    result = run_code(code)
    assert result["error"] == False
    assert "-2" in result["stdout"]
    print(f"✅ Numpy test passed. Output: {result['stdout']}")


def test_sympy_works():
    code = """
from sympy import symbols, solve
x = symbols('x')
solution = solve(x**2 - 5*x + 6, x)
print(solution)
"""
    result = run_code(code)
    assert result["error"] == False
    assert "2" in result["stdout"]
    assert "3" in result["stdout"]
    print(f"✅ Sympy test passed. Output: {result['stdout']}")


def test_blocked_import_rejected():
    code = "import os\nprint(os.getcwd())"
    safe, reason = is_code_safe(code)
    assert safe == False
    assert "os" in reason
    print(f"✅ Security test passed. Reason: {reason}")


def test_timeout_works():
    code = "while True: pass"
    result = run_code(code, timeout=3)
    assert result["error"] == True
    assert "timed out" in result["stderr"]
    print("✅ Timeout test passed")