import docker
import tempfile
import os
from pathlib import Path
from typing import Dict, Optional
import time


class DockerTestExecutor:
    """Executes test suites in isolated Docker containers."""
    
    def __init__(self, image_name: str = "testrunner:latest", timeout: int = 30):
        """
        Initialize Docker test executor.
        
        Args:
            image_name: Name of Docker image to use for test execution
            timeout: Maximum execution time in seconds
        """
        self.image_name = image_name
        self.timeout = timeout
        self.client = docker.from_env()
        self._ensure_image_exists()
    
    def _ensure_image_exists(self):
        """Check if the test runner image exists, build if not."""
        try:
            self.client.images.get(self.image_name)
        except docker.errors.ImageNotFound:
            print(f"Image {self.image_name} not found. Building from Dockerfile.testrunner...")
            # look for Dockerfile.testrunner in parent directory
            dockerfile_path = Path(__file__).parent.parent / "Dockerfile.testrunner"
            if not dockerfile_path.exists():
                raise FileNotFoundError(
                    f"Dockerfile.testrunner not found at {dockerfile_path}. "
                    "Please create it before running tests."
                )
            
            # build the image
            self.client.images.build(
                path=str(dockerfile_path.parent),
                dockerfile="Dockerfile.testrunner",
                tag=self.image_name,
                rm=True
            )
            print(f"Successfully built {self.image_name}")
    
    def execute_tests(
        self, 
        test_code: str, 
        target_code: str,
        timeout: Optional[int] = None
    ) -> Dict:
        """
        Execute test suite against target code in a container.
        
        Args:
            test_code: The pytest test file content
            target_code: The implementation code to test
            timeout: Override default timeout for this execution
            
        Returns:
            Dict with:
                - 'passed': bool, whether all tests passed
                - 'exit_code': int, pytest exit code
                - 'output': str, stdout/stderr from pytest
                - 'error': Optional[str], error message if execution failed
        """
        timeout = timeout or self.timeout
        
        # create temp directory for this test run
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            
            # write test file
            test_file = tmpdir_path / "test_generated.py"
            test_file.write_text(test_code, encoding='utf-8')
            
            # write target code (implementation being tested)
            target_file = tmpdir_path / "solution.py"
            target_file.write_text(target_code, encoding='utf-8')
            
            try:
                # run container with mounted volume
                container = self.client.containers.run(
                    self.image_name,
                    command=["pytest", "test_generated.py", "-v", "--tb=short"],
                    volumes={str(tmpdir_path): {'bind': '/test_workspace', 'mode': 'rw'}},
                    working_dir="/test_workspace",
                    detach=True,
                    remove=False,  # we'll remove manually after getting logs
                    network_mode="none",  # no network access for security
                )
                
                # wait for container to finish
                result = container.wait(timeout=timeout)
                exit_code = result['StatusCode']
                
                # get output
                output = container.logs().decode('utf-8', errors='replace')
                
                # clean up container
                container.remove()
                
                # pytest exit codes: 0 = all passed, 1 = some failed, others = errors
                passed = (exit_code == 0)
                
                return {
                    'passed': passed,
                    'exit_code': exit_code,
                    'output': output,
                    'error': None
                }
                
            except docker.errors.ContainerError as e:
                return {
                    'passed': False,
                    'exit_code': e.exit_status,
                    'output': e.stderr.decode('utf-8', errors='replace') if e.stderr else '',
                    'error': f"Container error: {str(e)}"
                }
            except Exception as e:
                return {
                    'passed': False,
                    'exit_code': -1,
                    'output': '',
                    'error': f"Execution failed: {str(e)}"
                }
    
    def execute_test_suite(
        self,
        test_code: str,
        correct_code: str,
        perturbations: list[str]
    ) -> Dict:
        """
        Execute test suite against correct code and all perturbations.
        
        Args:
            test_code: The pytest test file content
            correct_code: The correct implementation
            perturbations: List of 5 buggy implementations
            
        Returns:
            Dict with:
                - 'correct_passed': bool, whether tests pass on correct code
                - 'detections': list[bool], whether each perturbation was caught
                - 'detection_rate': float, fraction of perturbations caught
                - 'results': dict with detailed results for each execution
        """
        results = {}
        
        # first, test against correct implementation
        correct_result = self.execute_tests(test_code, correct_code)
        results['correct'] = correct_result
        correct_passed = correct_result['passed']
        
        # test against each perturbation
        detections = []
        perturbation_results = []
        
        for i, perturb_code in enumerate(perturbations):
            perturb_result = self.execute_tests(test_code, perturb_code)
            perturbation_results.append(perturb_result)
            
            # perturbation is "detected" if at least one test fails
            detected = not perturb_result['passed']
            detections.append(detected)
            
            results[f'perturbation_{i}'] = perturb_result
        
        detection_rate = sum(detections) / len(detections) if detections else 0.0
        
        return {
            'correct_passed': correct_passed,
            'detections': detections,
            'detection_rate': detection_rate,
            'results': results
        }
    
    def cleanup(self):
        """Clean up Docker client connection."""
        self.client.close()

