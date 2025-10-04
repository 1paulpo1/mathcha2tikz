#!/usr/bin/env python3
"""Thin wrapper to run the interactive CLI from `mathcha2tikz` module."""
import sys

from mathcha2tikz import main as cli_main

if __name__ == '__main__':
    sys.exit(cli_main())
