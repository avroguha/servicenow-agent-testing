#!/usr/bin/env python3
"""Entry point: python acctest.py <command>. See acctest/cli.py."""
import sys
from acctest.cli import main

if __name__ == "__main__":
    sys.exit(main())
