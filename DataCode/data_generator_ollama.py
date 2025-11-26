#!/usr/bin/env python3
"""
Script to generate code perturbations using Ollama (free local LLM).
Given a specification and correct implementation, generates subtle bugs and variations.
"""

import json
import argparse
import requests
import ast
import codecs


def generate_perturbations_ollama(
    specification: str,
    code: str,
    model: str = "deepseek-coder:6.7b",
    num_perturbations: int = 5
) -> list[str]:
    """
    Generate code perturbations using Ollama API.
    Generates exactly 5 perturbations, one for each category:
    1. Logic errors
    2. Boundary errors
    3. Type errors
    4. Incomplete implementations
    5. Performance bugs
    
    Args:
        specification: Natural language description of what the code should do
        code: The correct implementation
        model: Ollama model to use
        num_perturbations: Number of perturbations to generate (default: 5, always generates 5)
    
    Returns:
        List of perturbed code strings (always 5 items, one per category)
    """
    
    prompt = f"""Given the following specification and correct implementation, generate EXACTLY 5 perturbations of the code, one for each category below IN THIS EXACT ORDER:

1. **Logic errors:** Wrong operators (e.g., + instead of -, < instead of <=), incorrect conditionals
2. **Boundary errors:** Off-by-one errors, empty input mishandling, index errors
3. **Type errors:** Missing type checks, wrong type conversions, assuming wrong types
4. **Incomplete implementations:** Missing edge case handling, incomplete loop conditions
5. **Performance bugs:** Inefficient algorithms, redundant computations, wrong algorithmic approach

Each perturbation should:
- Introduce ONLY the type of bug for its category
- Maintain the same function signature
- Look plausible but produce incorrect results
- Be syntactically valid Python code
- Be a complete, self-contained function

Specification: {specification}

Correct Implementation:
```python
{code}
```

CRITICAL: Return ONLY a valid JSON array. Escape all special characters properly. Use double quotes, not single quotes.

Format (MUST be valid JSON):
[
  "def example(): ...",
  "def example(): ...",
  "def example(): ...",
  "def example(): ...",
  "def example(): ..."
]

DO NOT include explanations, markdown, or any text outside the JSON array."""

    # Call Ollama API
    response = requests.post(
        'http://localhost:11434/api/generate',
        json={
            'model': model,
            'prompt': prompt,
            'stream': False,
            'options': {
                'temperature': 0.7,
                'top_p': 0.9,
            }
        }
    )
    
    if response.status_code != 200:
        raise Exception(f"Ollama API error: {response.status_code} - {response.text}")
    
    # Extract the response text
    response_text = response.json()['response'].strip()
    
    # Remove markdown code blocks if present
    if response_text.startswith("```"):
        lines = response_text.split("\n")
        # Find JSON content between code blocks
        json_start = 1
        json_end = len(lines) - 1
        for i, line in enumerate(lines):
            if line.strip().startswith("["):
                json_start = i
                break
        for i in range(len(lines) - 1, -1, -1):
            if lines[i].strip().endswith("]"):
                json_end = i + 1
                break
        response_text = "\n".join(lines[json_start:json_end])
    
    # Parse JSON response with error handling
    try:
        # Try standard JSON parsing first
        perturbations = json.loads(response_text)
        if len(perturbations) != 5:
            print(f"Warning: Expected 5 perturbations, got {len(perturbations)}")
        return perturbations
    except json.JSONDecodeError as e:
        # Try to fix common issues
        try:
            # Attempt to decode raw strings (fix escape sequences)
            import codecs
            fixed_text = codecs.decode(response_text, 'unicode_escape')
            perturbations = json.loads(fixed_text)
            if len(perturbations) != 5:
                print(f"Warning: Expected 5 perturbations, got {len(perturbations)}")
            return perturbations
        except:
            pass
        
        # If still failing, try using ast.literal_eval as fallback
        try:
            import ast
            perturbations = ast.literal_eval(response_text)
            if isinstance(perturbations, list):
                if len(perturbations) != 5:
                    print(f"Warning: Expected 5 perturbations, got {len(perturbations)}")
                return perturbations
        except:
            pass
        
        print(f"Error parsing JSON response: {e}")
        print(f"Response was: {response_text[:500]}...")
        
        # Return empty list to continue processing other examples
        print(f"Skipping this example due to parsing error")
        return []


def process_examples(
    input_data: list[dict], 
    model: str = "deepseek-coder:6.7b"
) -> list[dict]:
    """
    Process multiple examples and generate perturbations for each.
    Always generates exactly 5 perturbations per example (one per category).
    
    Args:
        input_data: List of dicts with 'specification' and 'code' keys
        model: Ollama model to use
    
    Returns:
        List of dicts with added 'perturbations' key
    """
    results = []
    
    # Define categories
    categories = [
        "Logic errors",
        "Boundary errors", 
        "Type errors",
        "Incomplete implementations",
        "Performance bugs"
    ]
    
    for i, example in enumerate(input_data):
        print(f"Processing example {i+1}/{len(input_data)}...")
        
        perturbations = generate_perturbations_ollama(
            specification=example["specification"],
            code=example["code"],
            model=model
        )
        
        # Skip if perturbations failed to generate
        if not perturbations or len(perturbations) == 0:
            print(f"  Skipped due to generation error")
            continue
        
        result = {
            "specification": example["specification"],
            "code": example["code"],
            "perturbations": perturbations,
            "perturbation_categories": categories
        }
        results.append(result)
        
        print(f"  Generated {len(perturbations)} perturbations across {len(categories)} categories")
    
    return results


def main():
    parser = argparse.ArgumentParser(
        description="Generate code perturbations using Ollama (free local LLM)"
    )
    parser.add_argument(
        "--input",
        "-i",
        required=True,
        help="Input JSON file with specifications and code"
    )
    parser.add_argument(
        "--output",
        "-o",
        required=True,
        help="Output JSON file for results"
    )
    parser.add_argument(
        "--model",
        "-m",
        default="deepseek-coder:6.7b",
        help="Ollama model to use (default: deepseek-coder:6.7b). Other options: codellama:13b, qwen2.5-coder:7b"
    )
    
    args = parser.parse_args()
    
    # Check if Ollama is running
    try:
        response = requests.get('http://localhost:11434/api/tags')
        if response.status_code != 200:
            print("Error: Ollama is not running. Please start Ollama first:")
            print("  ollama serve")
            return
    except requests.exceptions.ConnectionError:
        print("Error: Cannot connect to Ollama. Please make sure Ollama is installed and running:")
        print("  Install: curl -fsSL https://ollama.com/install.sh | sh")
        print("  Start: ollama serve")
        return
    
    # Load input data
    print(f"Loading input from {args.input}...")
    with open(args.input, 'r') as f:
        input_data = json.load(f)
    
    # Process examples
    print(f"Using model: {args.model}")
    results = process_examples(
        input_data=input_data,
        model=args.model
    )
    
    # Save results
    print(f"\nSaving results to {args.output}...")
    with open(args.output, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"Done! Processed {len(results)} examples.")


if __name__ == "__main__":
    main()