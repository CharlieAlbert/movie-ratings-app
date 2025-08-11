#!/usr/bin/env python3
import sys
import os

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

# Import and run the app
from movie_app import main

if __name__ == "__main__":
    main()
