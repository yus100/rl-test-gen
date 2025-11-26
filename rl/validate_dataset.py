"""
Utility script to validate problem JSON files before using them.
Checks schema, perturbation count, and code syntax.
"""

import json
import sys
from pathlib import Path
from typing import List, Tuple


def validate_json_file(filepath: Path) -> Tuple[bool, List[str]]:
    """
    Validate a single problem JSON file.
    
    Returns:
        (is_valid, list_of_errors)
    """
    errors = []
    
    # check file exists
    if not filepath.exists():
        return False, [f"File not found: {filepath}"]
    
    # parse JSON
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        return False, [f"Invalid JSON: {e}"]
    except Exception as e:
        return False, [f"Error reading file: {e}"]
    
    # check required fields
    required_fields = ['spec', 'problem', 'perturbations']
    for field in required_fields:
        if field not in data:
            errors.append(f"Missing required field: '{field}'")
    
    if errors:
        return False, errors
    
    # validate field types
    if not isinstance(data['spec'], str):
        errors.append("'spec' must be a string")
    elif len(data['spec'].strip()) == 0:
        errors.append("'spec' cannot be empty")
    
    if not isinstance(data['problem'], str):
        errors.append("'problem' must be a string")
    elif len(data['problem'].strip()) == 0:
        errors.append("'problem' cannot be empty")
    
    if not isinstance(data['perturbations'], list):
        errors.append("'perturbations' must be a list")
    else:
        # check perturbation count
        if len(data['perturbations']) != 5:
            errors.append(
                f"Expected exactly 5 perturbations, got {len(data['perturbations'])}"
            )
        
        # check each perturbation
        for i, perturb in enumerate(data['perturbations']):
            if not isinstance(perturb, str):
                errors.append(f"Perturbation {i} must be a string")
            elif len(perturb.strip()) == 0:
                errors.append(f"Perturbation {i} cannot be empty")
    
    # try to compile Python code (syntax check)
    try:
        compile(data['problem'], '<problem>', 'exec')
    except SyntaxError as e:
        errors.append(f"Syntax error in 'problem': {e}")
    
    for i, perturb in enumerate(data.get('perturbations', [])):
        if isinstance(perturb, str):
            try:
                compile(perturb, f'<perturbation_{i}>', 'exec')
            except SyntaxError as e:
                errors.append(f"Syntax error in perturbation {i}: {e}")
    
    return len(errors) == 0, errors


def main():
    print("=" * 60)
    print("Problem Dataset Validator")
    print("=" * 60)
    print()
    
    problems_dir = Path("problems")
    
    if not problems_dir.exists():
        print(f"✗ Directory not found: {problems_dir}")
        print("  Create it with: mkdir problems")
        return 1
    
    json_files = list(problems_dir.glob("*.json"))
    
    if not json_files:
        print(f"✗ No JSON files found in {problems_dir}")
        print("  Add your problem files to this directory")
        return 1
    
    print(f"Found {len(json_files)} JSON file(s) to validate\n")
    
    results = []
    for json_file in json_files:
        print(f"Validating {json_file.name}...")
        is_valid, errors = validate_json_file(json_file)
        results.append((json_file.name, is_valid, errors))
        
        if is_valid:
            print(f"  ✓ Valid")
        else:
            print(f"  ✗ Invalid ({len(errors)} error(s)):")
            for error in errors:
                print(f"    - {error}")
        print()
    
    # summary
    print("=" * 60)
    print("Validation Summary")
    print("=" * 60)
    
    valid_count = sum(1 for _, is_valid, _ in results if is_valid)
    invalid_count = len(results) - valid_count
    
    print(f"Total files: {len(results)}")
    print(f"✓ Valid: {valid_count}")
    print(f"✗ Invalid: {invalid_count}")
    
    if invalid_count == 0:
        print("\n✓ All files are valid! Ready to use.")
        return 0
    else:
        print(f"\n✗ {invalid_count} file(s) need fixing.")
        print("\nInvalid files:")
        for name, is_valid, errors in results:
            if not is_valid:
                print(f"  - {name}")
        return 1


if __name__ == "__main__":
    sys.exit(main())

