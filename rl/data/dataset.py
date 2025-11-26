import json
import os
from pathlib import Path
from typing import Dict, List, Optional
import random


class ProblemDataset:
    """Loads and manages problem JSONs for RL training."""
    
    def __init__(self, dataset_path: str):
        """
        Initialize dataset loader.
        
        Args:
            dataset_path: Path to directory containing problem JSON files
        """
        self.dataset_path = Path(dataset_path)
        self.problems: List[Dict] = []
        self._load_problems()
    
    def _load_problems(self):
        """Load all JSON files from dataset directory."""
        if not self.dataset_path.exists():
            raise ValueError(f"Dataset path does not exist: {self.dataset_path}")
        
        json_files = list(self.dataset_path.glob("*.json"))
        
        if not json_files:
            raise ValueError(f"No JSON files found in {self.dataset_path}")
        
        for json_file in json_files:
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    problem = json.load(f)
                    self._validate_problem(problem, json_file.name)
                    problem['_filename'] = json_file.name
                    self.problems.append(problem)
            except json.JSONDecodeError as e:
                print(f"Warning: Failed to parse {json_file.name}: {e}")
            except Exception as e:
                print(f"Warning: Error loading {json_file.name}: {e}")
        
        if not self.problems:
            raise ValueError("No valid problems loaded from dataset")
        
        print(f"Loaded {len(self.problems)} problems from {self.dataset_path}")
    
    def _validate_problem(self, problem: Dict, filename: str):
        """
        Validate that problem has required fields.
        
        Args:
            problem: Problem dictionary
            filename: Name of file being validated (for error messages)
        """
        required_fields = ['spec', 'problem', 'perturbations']
        
        for field in required_fields:
            if field not in problem:
                raise ValueError(f"{filename}: Missing required field '{field}'")
        
        if not isinstance(problem['perturbations'], list):
            raise ValueError(f"{filename}: 'perturbations' must be a list")
        
        if len(problem['perturbations']) != 5:
            raise ValueError(
                f"{filename}: Expected exactly 5 perturbations, got {len(problem['perturbations'])}"
            )
        
        # validate that spec and problem are strings
        if not isinstance(problem['spec'], str):
            raise ValueError(f"{filename}: 'spec' must be a string")
        
        if not isinstance(problem['problem'], str):
            raise ValueError(f"{filename}: 'problem' must be a string")
    
    def sample(self, seed: Optional[int] = None) -> Dict:
        """
        Sample a random problem from the dataset.
        
        Args:
            seed: Optional random seed for reproducibility
            
        Returns:
            Dictionary with 'spec', 'problem', 'perturbations', and '_filename'
        """
        if seed is not None:
            random.seed(seed)
        
        return random.choice(self.problems)
    
    def get_by_index(self, idx: int) -> Dict:
        """
        Get problem by index.
        
        Args:
            idx: Index of problem to retrieve
            
        Returns:
            Problem dictionary
        """
        return self.problems[idx]
    
    def __len__(self) -> int:
        """Return number of problems in dataset."""
        return len(self.problems)
    
    def __iter__(self):
        """Iterate over all problems."""
        return iter(self.problems)

