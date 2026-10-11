"""
Console script entry point for infrabuddy.
"""

import sys
import os

# Add the project root to the path so we can import the root main module
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

# Import and run the main function from the root main.py
from main import main

if __name__ == "__main__":
    main()