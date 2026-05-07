import numpy as np
import sympy as sp
from typing import Any


def check_no_nan_inf(output: str) -> tuple[bool, str]:
    """Check if output contains NaN or Inf values."""
    if "nan" in output.lower():
        return False, "Output contains NaN"
    if "inf" in output.lower():
        return False, "Output contains Inf"
    return True, "No NaN or Inf detected"


def extract_numbers(output: str) -> list[float]:
    """Extract all numbers from string output."""
    import re
    pattern = r"[-+]?\d*\.?\d+(?:[eE][-+]?\d+)?"
    matches = re.findall(pattern, output)
    numbers = []
    for m in matches:
        try:
            numbers.append(float(m))
        except ValueError:
            pass
    return numbers


def check_numerical_stability(numbers: list[float]) -> tuple[bool, str]:
    """Check if numbers are numerically stable."""
    if not numbers:
        return False, "No numbers found in output"
    
    arr = np.array(numbers)
    
    if np.any(np.isnan(arr)):
        return False, "NaN detected in numbers"
    if np.any(np.isinf(arr)):
        return False, "Inf detected in numbers"
    if np.any(np.abs(arr) > 1e15):
        return False, "Extremely large values detected"
    
    return True, f"Numbers are stable: {numbers[:5]}"


def check_output_non_empty(stdout: str) -> tuple[bool, str]:
    """Check if code produced any output."""
    if not stdout or stdout.strip() == "":
        return False, "No output produced"
    return True, "Output is non-empty"


def run_all_checks(stdout: str, stderr: str, error: bool) -> dict:
    """
    Run all mathematical checks and return a verification report.
    Returns a score from 0-100.
    """
    checks = {}
    score = 0
    total_checks = 4

    # Check 1: No execution error
    checks["no_execution_error"] = not error
    if not error:
        score += 25

    # Check 2: Output is non-empty
    passed, reason = check_output_non_empty(stdout)
    checks["non_empty_output"] = passed
    if passed:
        score += 25

    # Check 3: No NaN or Inf in output
    passed, reason = check_no_nan_inf(stdout)
    checks["no_nan_inf"] = passed
    if passed:
        score += 25

    # Check 4: Numerical stability
    numbers = extract_numbers(stdout)
    passed, reason = check_numerical_stability(numbers)
    checks["numerical_stability"] = passed
    if passed:
        score += 25

    return {
        "score": score,
        "passed": score >= 75,
        "checks": checks,
        "extracted_numbers": numbers[:10],
        "reasoning": f"Score {score}/100 based on {total_checks} checks"
    }