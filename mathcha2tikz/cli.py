#!/usr/bin/env python3
"""CLI entry point for Mathcha to TikZ Converter."""

from __future__ import annotations

import argparse
import logging
import os
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass, field
from typing import Dict, Literal


# Support running as "python mathcha2tikz/cli.py" and as a package module.
if __package__ in (None, ""):
    PACKAGE_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    if PACKAGE_ROOT not in sys.path:
        sys.path.insert(0, PACKAGE_ROOT)
    from mathcha2tikz.cli_io import (  # type: ignore[relative-import]
        get_stdin_input,
        get_clipboard_input,
        set_clipboard_output,
        get_editor_input,
    )
    from mathcha2tikz.commands import run_conversion, quick_convert  # type: ignore[relative-import]
    from mathcha2tikz.cli_menus import (  # type: ignore[relative-import]
        settings_menu as settings_menu_impl,
        debug_menu as debug_menu_impl,
        main_menu as main_menu_impl,
    )
else:
    from .cli_io import (
        get_stdin_input,
        get_clipboard_input,
        set_clipboard_output,
        get_editor_input,
    )
    from .commands import run_conversion, quick_convert
    from .cli_menus import (
        settings_menu as settings_menu_impl,
        debug_menu as debug_menu_impl,
        main_menu as main_menu_impl,
    )
logger = logging.getLogger('mathcha2tikz.cli')

VERSION = "0.1.0"


RenderMode = Literal['classic', 'obsidian']
InputMethod = Literal['clipboard', 'paste', 'editor']


@dataclass
class CLIContext:
    """Stores CLI settings and user context for the conversion pipeline."""

    render_mode: str = "Obsidian"  # Display value; renderer gets lowercase
    enabled_modules: Dict[str, bool] = field(default_factory=lambda: {
        'arrows': True,
        'styles': True,
        'shapes': True,
    })
    debug: bool = False
    per_module_debug: Dict[str, bool] = field(default_factory=dict)
    input_method: str = "clipboard"  # clipboard, paste, editor
    copy_to_clipboard: bool = True
    pipeline_config: Dict[str, Dict] = field(default_factory=lambda: {
        'parser_options': {},
        'detector_options': {},
        'processor_options': {},
        'renderer_options': {},
    })

    def __post_init__(self) -> None:
        self.pipeline_config['renderer_options']['render_mode'] = self.render_mode.lower()

    def __str__(self) -> str:
        return (
            f"Render Mode: {self.render_mode}\n"
            f"Enabled Modules: {self.enabled_modules}\n"
            f"Debug: {self.debug}\n"
            f"Per-Module Debug: {self.per_module_debug}\n"
            f"Quick Input Method: {self.input_method}"
        )


def show_intro() -> None:
    """Display introduction and usage examples."""
    intro = f"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                           mathcha2tikz v{VERSION}                                ║
║                    Convert Mathcha export to optimized TikZ                  ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""
    print(intro, file=sys.stderr)


def run_conversion(input_text: str, mode: str, context: CLIContext) -> int:
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


def quick_convert(context: CLIContext) -> None:
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


def settings_menu(context: CLIContext) -> None:
    return settings_menu_impl(context)


def debug_menu(context: CLIContext) -> None:
    return debug_menu_impl(context)


def main_menu(context: CLIContext) -> None:
    return main_menu_impl(context)


def main() -> int:
    """Main entry point for the CLI."""
    parser = argparse.ArgumentParser(
        prog="mathcha2tikz",
        description="Convert Mathcha TikZ export to optimized TikZ",
    )
    parser.add_argument("-m", "--mode", choices=["classic", "obsidian"], default="obsidian",
                        help="Output mode (default: obsidian)")
    parser.add_argument("-f", "--file", help="Path to input file with Mathcha TikZ code")
    parser.add_argument("-c", "--clipboard", action="store_true",
                        help="Read input from clipboard")
    parser.add_argument("-i", "--interactive", action="store_true",
                        help="Force interactive mode even with piped input")
    parser.add_argument("--no-intro", action="store_true", help="Do not show intro banner")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    parser.add_argument("--input-method", choices=["clipboard", "paste", "editor"], help="Set quick input method")
    parser.add_argument("--no-copy", action="store_true", help="Do not copy output to clipboard")

    args = parser.parse_args()

    # Configure logging now that we have args
    logging.basicConfig(
        level=logging.DEBUG if args.debug else logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[logging.StreamHandler(sys.stderr)],
    )

    context = CLIContext()
    context.debug = bool(args.debug)
    context.render_mode = args.mode.capitalize() if args.mode else context.render_mode
    if args.input_method:
        context.input_method = args.input_method
    context.copy_to_clipboard = not bool(args.no_copy)
    context.pipeline_config['renderer_options']['render_mode'] = context.render_mode.lower()

    has_stdin_input = not sys.stdin.isatty()
    if (args.file or args.clipboard or has_stdin_input) and not args.interactive:
        try:
            if args.file:
                with open(args.file, "r", encoding="utf-8") as fh:
                    input_text = fh.read()
            elif args.clipboard:
                input_text = get_clipboard_input()
                if not input_text.strip():
                    print("Error: No text found in clipboard", file=sys.stderr)
                    return 1
            else:
                input_text = sys.stdin.read()

            if not input_text.strip():
                print("Error: No input provided", file=sys.stderr)
                return 1

            return run_conversion(input_text, args.mode, context)

        except Exception as exc:
            logger.error("Failed to read input: %s", exc)
            print(f"Failed to read input: {exc}", file=sys.stderr)
            return 1

    if not args.no_intro:
        show_intro()
    try:
        main_menu(context)
    except KeyboardInterrupt:
        print("\nGoodbye!")
        return 0
    except Exception as exc:
        logger.error("Unexpected error: %s", exc, exc_info=True)
        print(f"An unexpected error occurred: {exc}")
        return 1
    return 0


__all__ = [
    "CLIContext",
    "debug_menu",
    "get_clipboard_input",
    "get_editor_input",
    "get_stdin_input",
    "main",
    "main_menu",
    "pipeline_config_menu",
    "quick_convert",
    "run_conversion",
    "set_clipboard_output",
    "show_intro",
]


if __name__ == "__main__":
    sys.exit(main())
