#!/usr/bin/env python3
"""
Script to convert dataset into input.json format for perturbation generation.
Extracts code and creates specifications from commit messages.
"""

import json
import pandas as pd
import argparse
import datasets
import os
import pandas as pd
from datasets import load_dataset

def extract_function_or_class(code: str) -> str:
    """
    Extract the first complete function or class from the code.
    Returns the full code if it's already a single function/class.
    """
    lines = code.strip().split('\n')
    
    # Try to find a function or class definition
    start_idx = None
    indent_level = None
    
    for i, line in enumerate(lines):
        stripped = line.lstrip()
        if stripped.startswith('def ') or stripped.startswith('class '):
            start_idx = i
            indent_level = len(line) - len(stripped)
            break
    
    if start_idx is None:
        # No function/class found, return the whole code
        return code
    
    # Find the end of the function/class
    end_idx = len(lines)
    for i in range(start_idx + 1, len(lines)):
        line = lines[i]
        if line.strip() == '':
            continue
        current_indent = len(line) - len(line.lstrip())
        if current_indent <= indent_level and line.strip():
            end_idx = i
            break
    
    return '\n'.join(lines[start_idx:end_idx])


def create_specification_from_message(message: str, subject: str) -> str:
    """
    Create a specification from commit message and subject.
    """
    # Clean up the message
    message = message.strip()
    subject = subject.strip()
    
    # If message is too long, use subject
    if len(message) > 200 or '\n' in message[:50]:
        spec = subject
    else:
        spec = message if message else subject
    
    # Clean up common git commit prefixes
    spec = spec.replace('Fix ', '').replace('fix ', '')
    spec = spec.replace('Add ', '').replace('add ', '')
    spec = spec.replace('Update ', '').replace('update ', '')
    spec = spec.replace('Remove ', '').replace('remove ', '')
    spec = spec.replace('Revert ', '').replace('revert ', '')
    
    # Capitalize first letter
    if spec:
        spec = spec[0].upper() + spec[1:]
    
    return spec if spec else "Implement the function correctly"


def is_valid_code(code: str) -> bool:
    """
    Check if code is valid Python and not too short/long.
    """
    if not code or len(code.strip()) < 20:
        return False
    
    if len(code) > 2000:  # Skip very long code
        return False
    
    # Must contain def or class
    if 'def ' not in code and 'class ' not in code:
        return False
    
    # Skip if it's just imports or comments
    lines = [l.strip() for l in code.split('\n') if l.strip()]
    code_lines = [l for l in lines if not l.startswith('#') and not l.startswith('import') and not l.startswith('from')]
    
    if len(code_lines) < 3:
        return False
    
    return True


def convert_dataset_to_input(df, output_file: str, num_examples: int = 100):
    """
    Convert dataset CSV to input JSON format.
    
    Args:
        csv_file: Path to input CSV file
        output_file: Path to output JSON file
        num_examples: Number of examples to generate
    """
    
    print(f"Total rows in dataset: {len(df)}")
    
    # Filter for Python files
    if 'lang' in df.columns:
        df = df[df['lang'] == 'Python']
        print(f"Python files: {len(df)}")
    
    examples = []
    processed = 0
    
    for idx, row in df.iterrows():
        if len(examples) >= num_examples:
            break
        
        processed += 1
        if processed % 100 == 0:
            print(f"Processed {processed} rows, collected {len(examples)} valid examples...")
        
        # Extract code
        code = row.get('new_contents', '')
        if not isinstance(code, str):
            continue
        
        # Validate code
        if not is_valid_code(code):
            continue
        
        # Extract first function or class
        code_snippet = extract_function_or_class(code)
        
        if not is_valid_code(code_snippet):
            continue
        
        # Create specification
        subject = row.get('subject', '')
        message = row.get('message', '')
        
        if not isinstance(subject, str):
            subject = ''
        if not isinstance(message, str):
            message = ''
        
        specification = create_specification_from_message(message, subject)
        
        # Add to examples
        example = {
            "id": idx,
            "specification": specification,
            "code": code_snippet
        }
        
        examples.append(example)
    
    print(f"\nCollected {len(examples)} valid examples")
    
    # Save to JSON
    print(f"Saving to {output_file}...")
    with open(output_file, 'w') as f:
        json.dump(examples, f, indent=2)
    
    print(f"Done! Generated {len(examples)} examples.")
    print(f"\nYou can now run:")
    print(f"  python3 generate_perturbations_ollama.py -i {output_file} -o output.json -m qwen2.5-coder:3b")


def main():
    
    # obtain commitpackFT
    if int(datasets.__version__.split('.')[0]) >= 3:
        print(f"Detected datasets version {datasets.__version__} loaded in memory.")
        print("Restarting runtime to apply the downgraded version... Please re-run this cell after the restart.")
        os.kill(os.getpid(), 9)

    # Load the 'python' subset in streaming mode
    # trust_remote_code=True is required for this dataset on older datasets versions
    dataset = load_dataset("bigcode/commitpackft", "python", split="train", streaming=True, trust_remote_code=True)

    # Fetch the first 5 examples
    data_sample = list(dataset.take(500))

    # Convert to DataFrame for a clear view of the columns
    df = pd.DataFrame(data_sample)
    
    parser = argparse.ArgumentParser(
        description="Convert dataset to input JSON for perturbation generation"
    )
    
    parser.add_argument(
        "--output",
        "-o",
        default="input.json",
        help="Output JSON file path (default: input.json)"
    )
    parser.add_argument(
        "--num-examples",
        "-n",
        type=int,
        default=100,
        help="Number of examples to generate (default: 100)"
    )
    
    args = parser.parse_args()
    
    convert_dataset_to_input(
        df=df,
        output_file=args.output,
        num_examples=args.num_examples
    )


if __name__ == "__main__":
    main()