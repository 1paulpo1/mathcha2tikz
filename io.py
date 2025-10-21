"""CLI IO helpers for clipboard, stdin, and editor interactions."""
from __future__ import annotations

import logging
import os
import platform
import shutil
import subprocess
import sys
import tempfile

logger = logging.getLogger('mathcha2tikz.cli_io')


def _is_wsl() -> bool:
    """Detect if running under Windows Subsystem for Linux (WSL)."""
    try:
        rel = platform.release().lower()
        if 'microsoft' in rel:
            return True
        with open('/proc/version', 'r', encoding='utf-8') as fh:
            return 'microsoft' in fh.read().lower()
    except Exception:
        return False


def _run_capture(cmd: list[str]) -> str:
    """Run command and return stdout on success, else empty string."""
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return result.stdout
    except Exception:
        return ""


def _run_send(cmd: list[str], text: str) -> bool:
    """Run command with input text; return True on success."""
    try:
        subprocess.run(cmd, input=text, text=True, check=True)
        return True
    except Exception:
        return False


def get_stdin_input(prompt: str = "") -> str:
    """Read from stdin with support for very long lines and piped input."""
    if prompt:
        print(prompt, file=sys.stderr)

    if not sys.stdin.isatty():
        try:
            return sys.stdin.read()
        except KeyboardInterrupt:
            print("\nInput interrupted.", file=sys.stderr)
            return ""
        except Exception as exc:  # pragma: no cover - defensive
            print(f"Failed to read from stdin: {exc}", file=sys.stderr)
            return ""

    print("Paste your input (press Enter twice or Ctrl+D to finish):", file=sys.stderr)
    lines = []
    try:
        while True:
            try:
                line = input()
                lines.append(line)
            except EOFError:
                break
            except KeyboardInterrupt:
                print("\nInput interrupted.", file=sys.stderr)
                return ""
    except Exception as exc:  # pragma: no cover - defensive
        print(f"Error reading input: {exc}", file=sys.stderr)

    return "\n".join(lines)


def get_clipboard_input() -> str:
    """Get text from system clipboard using pyperclip or system utilities."""
    try:
        import pyperclip  # type: ignore

        clipboard_text = pyperclip.paste()
        if clipboard_text and clipboard_text.strip():
            logger.debug("Clipboard read via pyperclip")
            return clipboard_text
        logger.debug("Clipboard is empty or whitespace (pyperclip)")
        return ""
    except ImportError:
        pass
    except Exception as exc:  # pragma: no cover - defensive
        logger.debug("Clipboard pyperclip read failed: %s", exc)

    # WSL: use Windows clipboard tools from Linux environment
    try:
        if _is_wsl():
            text = _run_capture(['powershell.exe', '-NoProfile', '-Command', 'Get-Clipboard'])
            if text.strip():
                logger.debug("Clipboard read via powershell.exe (WSL)")
                return text
    except Exception as exc:  # pragma: no cover - defensive
        logger.debug("WSL clipboard read failed: %s", exc)

    try:
        if sys.platform == "win32":
            result = subprocess.run(
                ['powershell', '-command', 'Get-Clipboard'],
                capture_output=True,
                text=True,
                check=True,
            )
            if result.stdout.strip():
                logger.debug("Clipboard read via PowerShell")
                return result.stdout
        elif sys.platform == "darwin":
            result = subprocess.run(['pbpaste'], capture_output=True, text=True, check=True)
            if result.stdout.strip():
                logger.debug("Clipboard read via pbpaste")
                return result.stdout
        else:
            # Wayland first
            text = _run_capture(['wl-paste', '-n'])
            if text.strip():
                logger.debug("Clipboard read via wl-paste")
                return text
            # X11 fallbacks
            for cmd in [['xclip', '-selection', 'clipboard', '-o'], ['xsel', '--clipboard', '--output']]:
                try:
                    result = subprocess.run(cmd, capture_output=True, text=True, check=True)
                    if result.stdout.strip():
                        logger.debug("Clipboard read via %s", cmd[0])
                        return result.stdout
                except (subprocess.CalledProcessError, FileNotFoundError):
                    continue
    except Exception as exc:  # pragma: no cover - defensive
        logger.debug("Clipboard fallback failed: %s", exc)

    print("Error: Could not access clipboard. Please install pyperclip for better clipboard support.", file=sys.stderr)
    print("   pip install pyperclip", file=sys.stderr)
    return ""


def set_clipboard_output(text: str) -> bool:
    """Attempt to copy `text` to the system clipboard. Returns True on success."""
    if not text:
        return False

    try:
        import pyperclip  # type: ignore

        pyperclip.copy(text)
        logger.debug("Clipboard write via pyperclip")
        return True
    except ImportError:
        pass
    except Exception as exc:  # pragma: no cover - defensive
        logger.debug("Clipboard pyperclip copy failed: %s", exc)

    # WSL: try Windows clipboard from Linux environment
    try:
        if _is_wsl():
            if _run_send(['clip.exe'], text):
                logger.debug("Clipboard write via clip.exe (WSL)")
                return True
            if _run_send(['powershell.exe', '-NoProfile', '-Command', 'Set-Clipboard'], text):
                logger.debug("Clipboard write via powershell.exe (WSL)")
                return True
    except Exception as exc:  # pragma: no cover - defensive
        logger.debug("WSL clipboard write failed: %s", exc)

    try:
        if sys.platform == "win32":
            subprocess.run(
                ['powershell', '-command', 'Set-Clipboard'],
                input=text,
                text=True,
                check=True,
            )
            logger.debug("Clipboard write via PowerShell")
            return True
        elif sys.platform == "darwin":
            subprocess.run(['pbcopy'], input=text, text=True, check=True)
            logger.debug("Clipboard write via pbcopy")
            return True
        else:
            # Wayland first
            if _run_send(['wl-copy'], text):
                logger.debug("Clipboard write via wl-copy")
                return True
            # X11 fallbacks
            for cmd in [['xclip', '-selection', 'clipboard'], ['xsel', '--clipboard', '--input']]:
                try:
                    subprocess.run(cmd, input=text, text=True, check=True)
                    logger.debug("Clipboard write via %s", cmd[0])
                    return True
                except (subprocess.CalledProcessError, FileNotFoundError) as exc:
                    logger.debug("Clipboard command %s failed: %s", cmd[0], exc)
                    continue
    except Exception as exc:  # pragma: no cover - defensive
        logger.debug("Clipboard fallback write failed: %s", exc)

    return False


def get_editor_input(initial_text: str = "") -> str:
    """Open user's editor to capture large input."""
    editor = os.environ.get("EDITOR")
    if not editor:
        editor = shutil.which("nano") or shutil.which("vi") or "vi"

    with tempfile.NamedTemporaryFile(delete=False, suffix=".tikz", mode="w+", encoding="utf-8") as tf:
        temp_path = tf.name
        if initial_text:
            tf.write(initial_text)
            tf.flush()

    try:
        subprocess.run([editor, temp_path], check=True)
        with open(temp_path, "r", encoding="utf-8") as fh:
            return fh.read()
    except subprocess.CalledProcessError as exc:
        print(f"Editor failed: {exc}", file=sys.stderr)
        return ""
    except Exception as exc:
        print(f"Failed to use editor: {exc}", file=sys.stderr)
        return ""
    finally:
        try:
            os.remove(temp_path)
        except Exception:  # pragma: no cover - defensive
            pass
