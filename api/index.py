import os
import sys

# Ensure the root directory is in the python path so it can import app.py
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app
