# mathcha2tikz Workflow and Architecture

 This document describes the current conversion pipeline, key modules, and extensibility points as of Oct 2025.

## High-level Pipeline

 1. **Input acquisition**
  - CLI entry (canonical): `python -m mathcha2tikz`
  - Console script: `mathcha2tikz` (entry point -> `mathcha2tikz.CLI:main`)
  - Python API: use `core.converter.Converter` or `from mathcha2tikz import convert`
  - Clipboard/editor/stdin helpers: `mathcha2tikz/io.py`
  - Menus (interactive): `mathcha2tikz/menus.py`
2. **Detection & Parsing**
   - Shapes are detected and dispatched to specialized parsers
   - Current shape coverage:
     - `Straight Lines`: `modules/shapes/lines/straight/straight_parser.py`
     - `Curve Lines`: `modules/shapes/lines/curve/curve_parser.py`
     - `Ellipse/Circle`: `modules/shapes/ellipse/ellipse_parser.py`
     - `Arc`: `modules/shapes/arc/arc_parser.py`
   - Straight: `StraightArrowInfo` and `StraightMidArrow` (`ArrowDirection = Literal['<','>']`).
   - Curve/Arc: `TypedDict` payloads with explicit fields; directions aligned to `ArrowDirection`.
 
## CLI layout
 - `mathcha2tikz/CLI.py`: entrypoint (argparse, logging, context wiring) with Obsidian as default mode.
 - `mathcha2tikz/commands.py`: `run_conversion()`, `quick_convert()`.
 - `mathcha2tikz/io.py`: stdin/clipboard/editor helpers.
 - `mathcha2tikz/menus.py`: interactive menus; only core items are exposed now:
   - Settings: Render Mode, Input Method (module toggles and pipeline configuration hidden).
   - Debug: Global debug toggle (per-module debug UI hidden).
 
## Tests

{{ ... }}
- Unit tests for post-processors: dash normalization, deduplication, exact-name conversion
  - Legacy imports of `mathcha2tikz.utils.*` were removed. Modules now import helpers directly from top-level `utils.*`.

---

# Full Workflow Specification (Detailed)


## 1. CLI and IO Layer

- Entrypoints
  - Console script: `mathcha2tikz` -> `mathcha2tikz.CLI:main`.
  - Module invocation: `python -m mathcha2tikz`
- Main module: `mathcha2tikz/CLI.py`
  - Defines `CLIContext` for UI state: render mode, input method, debug, clipboard toggle, pipeline config.
  - Flags (subset): `--mode`, `--file`, `--clipboard`, `--interactive`, `--no-intro`, `--input-method`, `--debug`, `--no-copy`.
  - Delegates conversion to `mathcha2tikz/commands.py` (`run_conversion`, `quick_convert`).
- IO utilities: `mathcha2tikz/io.py`
  - `get_clipboard_input()` and `set_clipboard_output()` use `pyperclip` when available, otherwise OS fallbacks (`pbpaste/pbcopy`, PowerShell, `xclip/xsel`).
{{ ... }}
  styles/fillings/       (opacity_postprocessor)
  styles/dashes/         (dash_postprocessor, utils)
utils/
  geometry/              (shared_arrow_logic, bezier, base_geometry, ...)
  maintenance/           (get_color.py)
```
