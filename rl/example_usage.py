"""
Example script demonstrating how to use the TestGenEnv.

This script shows:
1. How to initialize the environment
2. How to reset and get a problem
3. How to generate a test suite (stubbed with a simple example)
4. How to step through the environment and get rewards
"""

from env.test_gen_env import TestGenEnv
import json


def generate_stub_test(spec: str, correct_code: str) -> str:
    """
    Stub test generator - in practice this would be an LLM.
    
    For demonstration, we generate a simple test that imports the solution
    and runs a basic assertion.
    """
    # extract function name from correct_code (very naive parsing)
    lines = correct_code.strip().split('\n')
    func_name = None
    for line in lines:
        if line.strip().startswith('def '):
            func_name = line.strip().split('def ')[1].split('(')[0]
            break
    
    if func_name is None:
        func_name = "solution_function"
    
    # generate a simple test
    test_code = f"""
from solution import {func_name}

def test_basic():
    # stub test - in real usage, LLM would generate comprehensive tests
    result = {func_name}(1)
    assert result is not None
    
def test_edge_case():
    # another stub test
    result = {func_name}(0)
    assert result is not None
"""
    
    return test_code


def main():
    print("=" * 60)
    print("TestGenEnv Example Usage")
    print("=" * 60)
    
    # initialize environment
    # NOTE: You need to have your problem JSONs in a 'problems' directory
    dataset_path = "./problems"
    
    print(f"\n1. Initializing environment with dataset: {dataset_path}")
    try:
        env = TestGenEnv(dataset_path=dataset_path, seed=42)
        print(f"   ✓ Environment initialized successfully")
        print(f"   ✓ Loaded {len(env.dataset)} problems")
    except Exception as e:
        print(f"   ✗ Failed to initialize: {e}")
        print("\nNote: Make sure you have:")
        print("  - A 'problems' directory with JSON files")
        print("  - Docker installed and running")
        print("  - Built the testrunner image (or it will auto-build)")
        return
    
    # reset to get first problem
    print("\n2. Resetting environment to sample a problem")
    obs, info = env.reset(seed=42)
    
    print(f"   Problem file: {info['problem_file']}")
    print(f"   Spec preview: {obs['spec'][:100]}...")
    print(f"   Code preview: {obs['correct_code'][:100]}...")
    
    # generate test suite (stubbed)
    print("\n3. Generating test suite (using stub generator)")
    test_suite = generate_stub_test(obs['spec'], obs['correct_code'])
    print(f"   Generated {len(test_suite)} characters of test code")
    print(f"   Test preview:\n{test_suite[:200]}...")
    
    # execute step
    print("\n4. Executing test suite and computing reward")
    print("   (This will run Docker containers - may take a moment...)")
    
    try:
        obs_next, reward, terminated, truncated, info = env.step(test_suite)
        
        print(f"\n   Results:")
        print(f"   ✓ Reward: {reward:.3f}")
        print(f"   ✓ Tests passed on correct code: {info['correct_passed']}")
        print(f"   ✓ Perturbations detected: {sum(info['detections'])}/5")
        print(f"   ✓ Detection rate: {info['detection_rate']:.1%}")
        print(f"   ✓ Individual detections: {info['detections']}")
        
        # interpret reward
        if reward == -1.0:
            print("\n   ⚠ False positive: tests rejected correct implementation")
        elif reward == 0.0:
            print("\n   ⚠ No bugs detected: tests may be too weak")
        elif reward < 0.5:
            print("\n   ⚠ Low detection rate: tests caught some bugs but missed others")
        elif reward < 1.0:
            print("\n   ✓ Good detection rate: tests caught most bugs")
        else:
            print("\n   ✓ Perfect score: tests caught all bugs!")
        
    except Exception as e:
        print(f"   ✗ Execution failed: {e}")
        import traceback
        traceback.print_exc()
    
    # cleanup
    print("\n5. Cleaning up")
    env.close()
    print("   ✓ Environment closed")
    
    print("\n" + "=" * 60)
    print("Example complete!")
    print("=" * 60)
    
    print("\nNext steps:")
    print("  - Replace stub generator with actual LLM")
    print("  - Integrate with GRPO training loop")
    print("  - Run on full dataset for training")


if __name__ == "__main__":
    main()

