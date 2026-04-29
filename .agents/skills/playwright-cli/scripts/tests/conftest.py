"""Shared test configuration."""

import sys
from pathlib import Path

# Make src/ importable (tests/conftest.py → src/)
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / 'src'))
