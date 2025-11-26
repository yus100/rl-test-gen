"""
Quick installation test to verify everything is set up correctly.
Run this after setup to ensure all components are working.
"""

import sys
from pathlib import Path


def test_imports():
    """Test that all required packages can be imported."""
    print("Testing imports...")
    try:
        import gymnasium
        print("  ✓ gymnasium")
    except ImportError as e:
        print(f"  ✗ gymnasium: {e}")
        return False
    
    try:
        import numpy
        print("  ✓ numpy")
    except ImportError as e:
        print(f"  ✗ numpy: {e}")
        return False
    
    try:
        import docker
        print("  ✓ docker")
    except ImportError as e:
        print(f"  ✗ docker: {e}")
        return False
    
    return True


def test_docker():
    """Test that Docker is accessible."""
    print("\nTesting Docker...")
    try:
        import docker
        client = docker.from_env()
        client.ping()
        print("  ✓ Docker daemon is running")
        
        # check for test runner image
        try:
            client.images.get("testrunner:latest")
            print("  ✓ testrunner:latest image exists")
        except docker.errors.ImageNotFound:
            print("  ⚠ testrunner:latest image not found")
            print("    Run: docker build -f Dockerfile.testrunner -t testrunner:latest .")
        
        client.close()
        return True
    except Exception as e:
        print(f"  ✗ Docker error: {e}")
        return False


def test_project_structure():
    """Test that project files exist."""
    print("\nTesting project structure...")
    
    required_files = [
        "data/dataset.py",
        "executor/docker_runner.py",
        "env/test_gen_env.py",
        "Dockerfile.testrunner",
        "requirements.txt"
    ]
    
    all_exist = True
    for file_path in required_files:
        if Path(file_path).exists():
            print(f"  ✓ {file_path}")
        else:
            print(f"  ✗ {file_path} not found")
            all_exist = False
    
    # check problems directory
    if Path("problems").exists():
        json_files = list(Path("problems").glob("*.json"))
        print(f"  ✓ problems/ directory ({len(json_files)} JSON files)")
        if len(json_files) == 0:
            print("    ⚠ No problem files found. Add JSON files to problems/")
    else:
        print("  ✗ problems/ directory not found")
        all_exist = False
    
    return all_exist


def test_dataset_loading():
    """Test that dataset can be loaded."""
    print("\nTesting dataset loading...")
    try:
        from data.dataset import ProblemDataset
        
        if not Path("problems").exists() or not list(Path("problems").glob("*.json")):
            print("  ⚠ Skipping (no problem files)")
            return True
        
        dataset = ProblemDataset("problems")
        print(f"  ✓ Loaded {len(dataset)} problems")
        
        # test sampling
        problem = dataset.sample()
        print(f"  ✓ Can sample problems")
        
        # validate structure
        assert 'spec' in problem
        assert 'problem' in problem
        assert 'perturbations' in problem
        assert len(problem['perturbations']) == 5
        print(f"  ✓ Problem structure is valid")
        
        return True
    except Exception as e:
        print(f"  ✗ Dataset loading failed: {e}")
        return False


def main():
    print("=" * 60)
    print("RL Test Gen Environment - Installation Test")
    print("=" * 60)
    print()
    
    results = []
    
    # run tests
    results.append(("Imports", test_imports()))
    results.append(("Docker", test_docker()))
    results.append(("Project Structure", test_project_structure()))
    results.append(("Dataset Loading", test_dataset_loading()))
    
    # summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    
    for name, passed in results:
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{status}: {name}")
    
    all_passed = all(result[1] for result in results)
    
    print("\n" + "=" * 60)
    if all_passed:
        print("✓ All tests passed! Installation is complete.")
        print("\nNext steps:")
        print("  1. Add your problem JSON files to problems/")
        print("  2. Run: python example_usage.py")
    else:
        print("✗ Some tests failed. Please check the errors above.")
        print("\nCommon fixes:")
        print("  - Install packages: pip install -r requirements.txt")
        print("  - Start Docker Desktop")
        print("  - Build image: docker build -f Dockerfile.testrunner -t testrunner:latest .")
    print("=" * 60)
    
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())

