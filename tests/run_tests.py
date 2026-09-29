"""
CareSim AI - Test Runner Script
Executes all unit and workflow tests via standard library unittest or pytest.
"""
import unittest
import sys
from pathlib import Path

# Add project root to sys.path
root_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(root_dir))

def run_suite():
    loader = unittest.TestLoader()
    suite = loader.discover(start_dir=str(root_dir / "tests"), pattern="test_*.py")
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    sys.exit(0 if result.wasSuccessful() else 1)

if __name__ == "__main__":
    run_suite()
