# Quick Start Guide

Get up and running with the RL Test Generation Environment in 5 minutes.

## Step 1: Setup Environment

### Windows
```bash
setup.bat
```

### Linux/Mac
```bash
chmod +x setup.sh
./setup.sh
```

This will:
- Create a Python virtual environment
- Install all required packages
- Build the Docker test runner image
- Create the `problems` directory

## Step 2: Prepare Your Dataset

Place your problem JSON files in the `problems/` directory. Each file should have:

```json
{
  "spec": "Your function specification...",
  "problem": "def your_function():\n    # correct implementation\n    pass",
  "perturbations": [
    "# buggy version 1 (logic error)",
    "# buggy version 2 (boundary error)", 
    "# buggy version 3 (type error)",
    "# buggy version 4 (incomplete)",
    "# buggy version 5 (performance bug)"
  ]
}
```

**Note:** An example problem is already provided at `problems/example_problem.json`

## Step 3: Run the Example

```bash
# activate virtual environment if not already active
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate.bat  # Windows

# run example
python example_usage.py
```

This will:
1. Load a problem from your dataset
2. Generate a stub test suite
3. Execute tests in Docker containers
4. Display the reward and detection breakdown

## Step 4: Integrate Your LLM

Replace the stub generator in your training code:

```python
from env.test_gen_env import TestGenEnv

env = TestGenEnv(dataset_path="./problems")

for episode in range(num_episodes):
    obs, info = env.reset()
    
    # YOUR LLM HERE - replace stub generator
    test_suite = your_llm.generate(
        prompt=f"Spec: {obs['spec']}\n\nCode: {obs['correct_code']}\n\nGenerate pytest tests:"
    )
    
    # get reward
    _, reward, _, _, info = env.step(test_suite)
    
    # update your model
    your_llm.update(reward)
    
    print(f"Episode {episode}: Reward={reward:.3f}, Detected={sum(info['detections'])}/5")

env.close()
```

## Expected Output

When running the example, you should see:

```
============================================================
TestGenEnv Example Usage
============================================================

1. Initializing environment with dataset: ./problems
   ✓ Environment initialized successfully
   ✓ Loaded 1 problems

2. Resetting environment to sample a problem
   Problem file: example_problem.json
   Spec preview: Write a function `add_numbers(a, b)` that takes two integers...
   Code preview: def add_numbers(a, b):...

3. Generating test suite (using stub generator)
   Generated 234 characters of test code
   Test preview:
from solution import add_numbers...

4. Executing test suite and computing reward
   (This will run Docker containers - may take a moment...)

   Results:
   ✓ Reward: 0.400
   ✓ Tests passed on correct code: True
   ✓ Perturbations detected: 2/5
   ✓ Detection rate: 40.0%
   ✓ Individual detections: [True, False, True, False, False]

   ⚠ Low detection rate: tests caught some bugs but missed others

5. Cleaning up
   ✓ Environment closed

============================================================
Example complete!
============================================================
```

## Troubleshooting

### "Docker daemon is not running"
- Start Docker Desktop (Windows/Mac) or Docker service (Linux)
- Verify with: `docker ps`

### "No JSON files found in ./problems"
- Make sure you have at least one JSON file in the `problems/` directory
- Check that files have `.json` extension
- Use the provided `example_problem.json` as a template

### "Image testrunner:latest not found"
- Run: `docker build -f Dockerfile.testrunner -t testrunner:latest .`
- Or re-run the setup script

### Tests timeout
- Increase timeout: `TestGenEnv(dataset_path="./problems", test_timeout=60)`
- Check if generated tests have infinite loops

## Next Steps

1. **Add more problems**: Populate `problems/` with your full dataset
2. **Integrate LLM**: Replace stub generator with Qwen 3 8B or your model
3. **Implement GRPO**: Add policy optimization training loop
4. **Scale up**: Run distributed training on full dataset
5. **Evaluate**: Test on benchmarks (UnleakedTestBench, TestGenEval, SWT-Bench)

## Resources

- Full documentation: [README.md](README.md)
- Proposal: [proposal.txt](proposal.txt)
- Example code: [example_usage.py](example_usage.py)

Happy training! 🚀

