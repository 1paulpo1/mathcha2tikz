"""Interactive CLI menus with simple IO, extracted from cli.py.
Each function operates on CLIContext and uses input()/print() for now.
Optionally, later we can inject IO streams for testing.
"""
from __future__ import annotations

import logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .CLI import CLIContext

logger = logging.getLogger('mathcha2tikz.cli_menus')


def settings_menu(context: 'CLIContext') -> None:
    while True:
        print("\nSETTINGS MENU\n" + "=" * 20)
        print(f"1. Select Render Mode (Current: {context.render_mode})")
        print(f"2. Select Quick Input Method (Current: {context.input_method.capitalize()})")
        print("3. Back")
        choice = input("Select an option: ").strip()
        if choice == "1":
            print("\nAvailable Render Modes: Classic, Obsidian")
            mode = input("Enter render mode: ").strip().capitalize()
            if mode in ["Classic", "Obsidian"]:
                context.render_mode = mode
                context.pipeline_config['renderer_options']['render_mode'] = mode.lower()
                print(f"Render mode set to {mode}")
            else:
                print("Invalid render mode.")
        elif choice == "2":
            print("\nQuick Input Methods: clipboard, paste, editor")
            method = input("Enter quick input method: ").strip().lower()
            if method in ["clipboard", "paste", "editor"]:
                context.input_method = method
                print(f"Quick input method set to {method.capitalize()}")
            else:
                print("Invalid input method.")
        elif choice == "3":
            break
        else:
            print("Invalid option.")


def debug_menu(context: 'CLIContext') -> None:
    while True:
        print("\nDEBUG OPTIONS\n" + "=" * 20)
        print(f"1. Toggle Full Debug (Current: {context.debug})")
        print("2. Back")
        choice = input("Select an option: ").strip()
        if choice == "1":
            context.debug = not context.debug
            print(f"Full debug set to {context.debug}")
            logging.getLogger().setLevel(logging.DEBUG if context.debug else logging.INFO)
        elif choice == "2":
            break
        else:
            print("Invalid option.")


def main_menu(context: 'CLIContext') -> None:
    while True:
        print("\n" + "=" * 80)
        print("MAIN MENU")
        print("=" * 80)
        print("A. Quick Convert (Paste & Convert)")
        print("B. Settings")
        print("C. Debug Options")
        print("D. About")
        print("Q. Quit")
        print("=" * 80)
        try:
            choice = input("\nSelect an option: ").strip().upper()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            break
        if choice == "A":
            from .commands import quick_convert  # lazy import to avoid cycles
            quick_convert(context)
        elif choice == "B":
            settings_menu(context)
        elif choice == "C":
            debug_menu(context)
        elif choice == "D":
            from .CLI import VERSION
            print(f"\nmathcha2tikz version {VERSION}")
            print("A tool to convert and optimize Mathcha TikZ code.")
            print("Supports various shapes, styles, and arrows.")
        elif choice == "Q":
            print("\nGoodbye!")
            break
        else:
            print("\nInvalid option. Please try again.")
