#!/usr/bin/env python3
"""Parse playwright-cli Gmail snapshot YAML and display emails.

Usage:
  python3 parse-gmail-snapshot.py <snapshot.yml> [--json] [--body] [--all]
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from pwcli.gmail.cli import main

sys.exit(main())
