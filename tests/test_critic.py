from sandbox.math_checker import (
    run_all_checks,
    extract_numbers,
    check_no_nan_inf,
    check_numerical_stability
)


def test_perfect_output_scores_100():
    result = run_all_checks(
        stdout="Eigenvalues: [1.5, 2.3, 0.8]",
        stderr="",
        error=False
    )
    assert result["score"] == 100
    print(f"✅ Perfect output: {result['score']}/100")


def test_error_output_scores_low():
    result = run_all_checks(
        stdout="",
        stderr="NameError: name x is not defined",
        error=True
    )
    assert result["score"] <= 25
    print(f"✅ Error output: {result['score']}/100")


def test_nan_detected():
    passed, reason = check_no_nan_inf("output: nan")
    assert passed == False
    assert "NaN" in reason
    print(f"✅ NaN detected: {reason}")


def test_numbers_extracted_correctly():
    numbers = extract_numbers("Result: [1.5, -2.3, 0.008]")
    assert 1.5 in numbers
    assert -2.3 in numbers
    print(f"✅ Extracted numbers: {numbers}")


def test_unstable_numbers_flagged():
    numbers = [1e16, 2.0, 3.0]
    passed, reason = check_numerical_stability(numbers)
    assert passed == False
    print(f"✅ Unstable numbers flagged: {reason}")