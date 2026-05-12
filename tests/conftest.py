"""Shared pytest fixtures."""
import sys
from pathlib import Path

# Make lib/ importable
sys.path.insert(0, str(Path(__file__).parent.parent))
