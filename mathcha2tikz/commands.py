"""CLI commands: run_conversion and quick_convert."""
from __future__ import annotations

import logging
import sys
from typing import TYPE_CHECKING

from core.converter import Converter
from .cli_io import (
    get_stdin_input,
    get_clipboard_input,
    set_clipboard_output,
    get_editor_input,
)

if TYPE_CHECKING:  # avoid runtime circular import
    from .cli import CLIContext

logger = logging.getLogger('mathcha2tikz.commands')


def run_conversion(input_text: str, mode: str, context: 'CLIContext') -> int:
    """Run conversion for given input_text and mode. Returns exit code."""
    if not input_text or not input_text.strip():
        print("No input provided.", file=sys.stderr)
        return 2

    if r"\begin{tikzpicture}" not in input_text and 'tikz' not in input_text.lower():
        print("Warning: Input does not appear to contain TikZ code", file=sys.stderr)
        print("Continuing anyway...\n", file=sys.stderr)

    logging.getLogger().setLevel(logging.DEBUG if context.debug else logging.INFO)

    try:
        converter = Converter(config=context.pipeline_config)
        result = converter.convert(input_text, mode=mode)
        if not result or not result.strip():
            print("Error: Conversion returned empty output", file=sys.stderr)
            return 3
        print(result)
        if context.copy_to_clipboard:
            if set_clipboard_output(result):
                logger.debug("Conversion output copied to clipboard")
                print("\nOutput copied to clipboard.", file=sys.stderr)
            else:
                logger.debug("Failed to copy conversion output to clipboard")
                print("\nWarning: Could not copy output to clipboard.", file=sys.stderr)
        return 0
    except Exception as exc:
        logger.error("Conversion error: %s", exc, exc_info=context.debug)
        print(f"Error during conversion: {exc}", file=sys.stderr)
        return 1


def quick_convert(context: 'CLIContext') -> None:
    """Quick convert mode - uses saved defaults for input/output."""
    try:
        print("\n" + "=" * 80)
        print("QUICK CONVERT MODE")
        print("=" * 80)

        input_method = context.input_method.lower() if context.input_method else "clipboard"
        mode = context.render_mode.lower() if context.render_mode else "classic"

        print(f"Input method: {input_method.capitalize()} (change via Settings)")
        print(f"Output mode: {mode.capitalize()} (change via Settings)")

        input_text = ""
        if input_method == "paste":
            input_text = get_stdin_input(
                f"\nPaste your Mathcha TikZ code below [Mode: {mode.capitalize()}]:\n" + "=" * 80
            )
        elif input_method == "editor":
            input_text = get_editor_input("% Paste Mathcha TikZ here\n")
        else:
            logger.debug("Reading from clipboard [Mode: %s]", mode.capitalize())
            input_text = get_clipboard_input()
            if not input_text.strip():
                print("No text found in clipboard. Falling back to manual paste.", file=sys.stderr)
                input_text = get_stdin_input("Please paste your Mathcha TikZ code:\n" + "=" * 80)

        if not input_text or not input_text.strip():
            print("No input provided.", file=sys.stderr)
            return

        print("\n" + "=" * 80, file=sys.stderr)
        print("CONVERTING...", file=sys.stderr)
        print("=" * 80, file=sys.stderr)

        exit_code = run_conversion(input_text, mode, context)
        if exit_code == 0:
            print("=" * 80, file=sys.stderr)
            print("CONVERSION COMPLETE", file=sys.stderr)

    except KeyboardInterrupt:
        print("\nConversion cancelled by user.", file=sys.stderr)
    except Exception as exc:
        logger.error("Error during conversion: %s", exc, exc_info=context.debug)
        print(f"\nError during conversion: {exc}", file=sys.stderr)
