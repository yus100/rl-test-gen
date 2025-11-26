"""
Test script to verify Docker container execution works correctly.
Uses hardcoded code and test cases to check pass/fail detection.
"""

from executor.docker_runner import DockerTestExecutor


def test_basic_execution():
    """Test that we can run tests and get pass/fail results."""
    print("=" * 60)
    print("Docker Execution Test")
    print("=" * 60)
    print()
    
    # initialize executor
    print("1. Initializing Docker executor...")
    try:
        executor = DockerTestExecutor(timeout=30)
        print("   ✓ Docker executor initialized")
    except Exception as e:
        print(f"   ✗ Failed to initialize: {e}")
        return False
    
    # test case 1: correct code with passing tests
    print("\n2. Test Case 1: Correct code with passing tests")
    correct_code = """
def add(a, b):
    return a + b

def multiply(a, b):
    return a * b
"""
    
    passing_tests = """
from solution import add, multiply

def test_add_positive():
    assert add(2, 3) == 5
    
def test_add_negative():
    assert add(-1, -1) == -2
    
def test_multiply():
    assert multiply(3, 4) == 12
"""
    
    print("   Running tests...")
    result = executor.execute_tests(passing_tests, correct_code)
    
    if result['passed']:
        print("   ✓ Tests passed (as expected)")
    else:
        print(f"   ✗ Tests failed unexpectedly")
        print(f"   Exit code: {result['exit_code']}")
        print(f"   Output: {result['output'][:200]}")
        return False
    
    # test case 2: buggy code with failing tests
    print("\n3. Test Case 2: Buggy code with failing tests")
    buggy_code = """
def add(a, b):
    return a - b  # wrong operator!

def multiply(a, b):
    return a * b
"""
    
    print("   Running tests...")
    result = executor.execute_tests(passing_tests, buggy_code)
    
    if not result['passed']:
        print("   ✓ Tests failed (as expected - bug detected)")
    else:
        print(f"   ✗ Tests passed unexpectedly (should have caught bug)")
        return False
    
    # test case 3: correct code with overly strict tests (false positive)
    print("\n4. Test Case 3: Correct code with overly strict tests")
    strict_tests = """
from solution import add

def test_add_wrong_expectation():
    assert add(2, 3) == 6  # wrong expectation
"""
    
    print("   Running tests...")
    result = executor.execute_tests(strict_tests, correct_code)
    
    if not result['passed']:
        print("   ✓ Tests failed (as expected - false positive detected)")
    else:
        print(f"   ✗ Tests passed unexpectedly")
        return False
    
    # test case 4: test full suite execution (correct + perturbations)
    print("\n5. Test Case 4: Full suite execution (correct + 5 perturbations)")
    
    perturbations = [
        # logic error
        """
def add(a, b):
    return a - b
def multiply(a, b):
    return a * b
""",
        # boundary error
        """
def add(a, b):
    return a + b + 1
def multiply(a, b):
    return a * b
""",
        # type error
        """
def add(a, b):
    return str(a) + str(b)
def multiply(a, b):
    return a * b
""",
        # incomplete (missing multiply)
        """
def add(a, b):
    return a + b
def multiply(a, b):
    return 0  # always returns 0
""",
        # performance bug (still correct but inefficient)
        """
def add(a, b):
    result = a
    for i in range(abs(b)):
        result += 1 if b > 0 else -1
    return result
def multiply(a, b):
    return a * b
"""
    ]
    
    print("   Running full test suite...")
    suite_result = executor.execute_test_suite(
        test_code=passing_tests,
        correct_code=correct_code,
        perturbations=perturbations
    )
    
    print(f"   Correct code passed: {suite_result['correct_passed']}")
    print(f"   Perturbations detected: {sum(suite_result['detections'])}/5")
    print(f"   Detection breakdown: {suite_result['detections']}")
    print(f"   Detection rate: {suite_result['detection_rate']:.1%}")
    
    # verify results make sense
    if not suite_result['correct_passed']:
        print("   ✗ Correct code should have passed")
        return False
    
    # we expect to catch logic, boundary, type, and incomplete errors
    # performance bug might not be caught since it's still functionally correct
    expected_detections = [True, True, True, True, False]
    
    if suite_result['detections'][:4] == expected_detections[:4]:
        print("   ✓ Detected expected bugs (logic, boundary, type, incomplete)")
    else:
        print(f"   ⚠ Detection pattern differs from expected")
        print(f"     Expected: {expected_detections}")
        print(f"     Got:      {suite_result['detections']}")
    
    # test case 5: syntax error in test code
    print("\n6. Test Case 5: Handling syntax errors in test code")
    bad_test = """
from solution import add

def test_syntax_error(
    # missing closing paren and body
"""
    
    print("   Running tests with syntax error...")
    result = executor.execute_tests(bad_test, correct_code)
    
    if not result['passed']:
        print("   ✓ Handled syntax error gracefully")
    else:
        print("   ⚠ Unexpected result with syntax error")
    
    # test case 6: test that imports work correctly
    print("\n7. Test Case 6: Testing imports and module structure")
    code_with_helper = """
def helper(x):
    return x * 2

def process(a, b):
    return helper(a) + helper(b)
"""
    
    tests_with_imports = """
from solution import process, helper

def test_helper():
    assert helper(5) == 10

def test_process():
    assert process(2, 3) == 10  # (2*2) + (3*2)
"""
    
    print("   Running tests with multiple imports...")
    result = executor.execute_tests(tests_with_imports, code_with_helper)
    
    if result['passed']:
        print("   ✓ Multiple imports work correctly")
    else:
        print(f"   ✗ Import test failed")
        print(f"   Output: {result['output'][:300]}")
        return False
    
    # cleanup
    print("\n8. Cleaning up...")
    executor.cleanup()
    print("   ✓ Cleanup complete")
    
    return True


def main():
    print("\nThis script tests the Docker execution system with hardcoded examples.\n")
    
    try:
        success = test_basic_execution()
        
        print("\n" + "=" * 60)
        if success:
            print("✓ All Docker execution tests passed!")
            print("\nThe Docker container system is working correctly:")
            print("  - Can execute tests and detect pass/fail")
            print("  - Can catch bugs in perturbations")
            print("  - Can detect false positives")
            print("  - Handles errors gracefully")
            print("  - Supports multiple imports")
        else:
            print("✗ Some tests failed. Check output above.")
        print("=" * 60)
        
        return 0 if success else 1
        
    except Exception as e:
        print("\n" + "=" * 60)
        print(f"✗ Test execution failed with error:")
        print(f"   {e}")
        print("=" * 60)
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    import sys
    sys.exit(main())

