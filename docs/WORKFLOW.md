# mathcha2tikz Workflow and Architecture
 This document describes the current conversion pipeline, key modules, and extensibility points as of Oct 2025.

## High-level Pipeline

 1. **Input acquisition**
   - CLI entry (canonical): `python -m mathcha2tikz.CLI`
   - CLI shim (backward-compat): `python -m mathcha2tikz.cli`
   - Console script: `mathcha2tikz` (via `setup.py` entry point -> `mathcha2tikz.CLI:main`)
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

- E2E tests for both modes (classic, obsidian)
- Unit tests for post-processors: dash normalization, deduplication, exact-name conversion
  - Some modules historically imported `mathcha2tikz.utils.style_utils` and `modules.shapes.lines.shared_arrow_logic`.
  - The project provides compatibility shims:
    - `mathcha2tikz/utils/style_utils.py` re-exports helpers from `utils/style_utils.py`.
    - `modules/shapes/lines/shared_arrow_logic.py` re-exports from `utils/geometry/shared_arrow_logic.py`.
  - These shims allow both legacy and current paths to work during migration to a fully modular layout.

---

# Full Workflow Specification (Detailed)

This section provides a precise, end-to-end description of how the program works today, including module paths, data contracts, registration, error handling, and extensibility guidelines.

## 1. CLI and IO Layer

- Entrypoints
  - Console script: `mathcha2tikz` -> `mathcha2tikz.CLI:main` (see `setup.py` `entry_points`).
  - Module invocations:
    - Canonical: `python -m mathcha2tikz.CLI`
    - Shim: `python -m mathcha2tikz.cli` (kept for backward-compat)
- Main module: `mathcha2tikz/CLI.py`
  - Defines `CLIContext` for UI state: render mode, input method, debug, clipboard toggle, pipeline config.
  - Flags (subset): `--mode`, `--file`, `--clipboard`, `--interactive`, `--no-intro`, `--input-method`, `--debug`, `--no-copy`.
  - Delegates conversion to `mathcha2tikz/commands.py` (`run_conversion`, `quick_convert`).
- IO utilities: `mathcha2tikz/io.py`
  - `get_clipboard_input()` and `set_clipboard_output()` use `pyperclip` when available, otherwise OS fallbacks (`pbpaste/pbcopy`, PowerShell, `xclip/xsel`).
  - `get_editor_input()` launches editor (`$EDITOR`, `nano`, `vi`) via tempfile.
- Menus: `mathcha2tikz/menus.py`
  - Provides settings and debug menus; currently only core items are exposed.

## 2. Conversion Pipeline Overview

High-level stages: `Parser → Detector → Processor → Renderer → PostProcessor → Output Composition`.

- Orchestration: `core/converter.py` `Converter`
  - Lazily registers built-ins via `ensure_builtin_processors_registered()` and `ensure_builtin_renderers_registered()`.
  - Raises on empty/failed stages with precise exception types from `core/exceptions.py`.

## 3. Parsing (`core/parser.py`)

- Input is split into shape blocks by scanning lines and grouping TikZ commands under leading annotation comments.
- `ShapeBlock` fields:
  - `raw_block`, `annotation`, `shape_type`, `shape_id`, `raw_shape_data`, `raw_arrows_data`.
- Supported annotation triggers (case-insensitive): `Arc`, `Straight Lines`, `Curve Lines`, `Circle`, `Ellipse`, `Text Node`, `Node`.
- Arrow extraction: `_is_arrow_line()` detects shift/rotate patterns typical for Mathcha arrowheads; those lines are moved into `raw_arrows_data`.

## 4. Detection (`core/detector.py`)

- Normalizes the annotation-derived shape name into canonical keys using `_CANONICAL_ALIASES` and `_ALIAS_LOOKUP`.
- Returns `types.SimpleNamespace` payloads with at least: `id`, `shape_type`, `annotation`, `raw_block`, optionally `raw_shape_data` and `raw_arrows_data`.

## 5. Processing (`core/processor.py`)

- Registry: `ProcessorRegistry`
  - `register()`, `register_fallback()`, `get_processor()` with normalization of keys (spaces/hyphens → underscores, lowercase).
  - Fallback: `RawPassthroughProcessor` for unknown/unsupported shapes.
- Registration: `register_builtin_processors()` imports and registers:
  - `StraightProcessor` (`modules/shapes/lines/straight/straight_processor.py`)
  - `CurveProcessor` (`modules/shapes/lines/curve/curve_processor.py`)
  - `EllipseProcessor` (`modules/shapes/ellipse/ellipse_processor.py`) — handles Ellipse/Circle
  - `ArcProcessor` (`modules/shapes/arc/arc_processor.py`)
- Shape processors contract:
  - Accept `shape_instance` (object or dict), robustly read via `getattr()`.
  - Parse raw block with shape-specific parser, process arrows, merge styles, and return dict with `tikz_code` and metadata (`start_point`, `end_point`, `id`, etc.).
- Arrow utilities:
  - Shared arrow parsing helpers in `utils/geometry/shared_arrow_logic.py`
  - Legacy import path shim: `modules/shapes/lines/shared_arrow_logic.py` re-exports these helpers.

## 6. Rendering (`core/renderer.py`)

- Registry: `RendererRegistry` mirrors processor registry behavior.
- Registration: `register_builtin_renderers()` wraps per-shape renderers into registry classes:
  - Straight: `modules/shapes/lines/straight/straight_renderer.py`
  - Ellipse/Circle: `modules/shapes/ellipse/ellipse_renderer.py`
  - Arc: `modules/shapes/arc/arc_renderer.py`
- `GlobalRenderer`
  - Normalizes render payload (`type`, `id`, styles), merges dict/list/`style_str` consistently.
  - Collects used colors from styles for downstream post-processing.
  - Applies template via `core/output_modes.py -> core/templates.py`.
- Output composition:
  - `compose_output(color_definitions, processed_body, mode)` assembles final output.
  - Classic mode splits out commented preamble hints and keeps `tikzpicture` minimal; Obsidian mode prepends active preamble and wraps in a document.

## 7. Post-processing (`core/postprocessing.py`)

Order is enforced in `PostProcessor.process()`:

1) Color
   - `modules/styles/colors/color_postprocessor.py`
   - Uses `ColorKDTree` (NumPy) for nearest named color lookup among `COLOR_DEFINITIONS`.
   - Returns `processed_code`, `color_definitions`, and stats.

2) Opacity
   - `modules/styles/fillings/opacity_postprocessor.py`
   - Removes `draw opacity=1`, preserves non-1 values, cleans style brackets.

3) Dash patterns
   - `modules/styles/dashes/dash_postprocessor.py`
   - De-duplicates multiple `dash pattern={...}` entries, normalizes pattern text, converts exact matches to named styles (`dashed`, `dotted`, etc.).

Finally, `Renderer.compose_output(...)` integrates color definitions and body per selected mode.

## 8. Output Modes (`core/templates.py` via `core/output_modes.py`)

- `classic` and `obsidian` immutable templates; application guarded for safety in `GlobalRenderer`.
- Classic: keeps output editor-friendly. Obsidian: ensures required libraries and document wrapper for TikZJaX.

## 9. Extending with a New Shape (Guidelines)

1) Create parser under `modules/shapes/<family>/<shape>/<shape>_parser.py` that extracts the main command, styles, and any arrow side-commands.
2) Create arrows helper if needed (e.g., `<shape>_arrows.py`) using helpers from `utils/geometry`.
3) Create renderer `<shape>_renderer.py` that accepts a normalized dict and returns TikZ code string or `{ 'tikz_code': ... }` dict.
4) Create processor `<shape>_processor.py` that wires parser → arrows → renderer and returns processed dict.
5) Register in `core/processor.register_builtin_processors()` and `core/renderer.register_builtin_renderers()` with the canonical shape names used by `core/detector.py`.

## 10. Error Handling and Diagnostics

- Parser raises `ParserError` on invalid input formatting.
- Detector proceeds conservatively; unresolved types become `'unknown'` and are handled by fallback processor if present.
- Processor stage raises `ProcessingError` for missing registrations or unexpected processing failures.
- Renderer raises `RenderingError` for missing renderer or generation errors.
- Common runtime warnings:
  - "Could not import built-in processors/renderers": verify compatibility shims and module paths.
  - "No processor/renderer registered for shape type ...": ensure registration and detector canonical names match.

## 11. Dependencies

- Runtime: `numpy` (used by ColorKDTree and some geometry helpers).
- Optional: `pyperclip` (clipboard I/O).
- Maintenance (not runtime): `requests`, `beautifulsoup4` (for color DB maintenance in `utils/maintenance/get_color.py`).
- Development: `pytest`, `pytest-cov`, `mypy`, `ruff`.

## 12. Directory Map (abridged)

```
core/
  converter.py, parser.py, detector.py, processor.py, renderer.py,
  postprocessing.py, templates.py, output_modes.py
mathcha2tikz/
  CLI.py, cli.py (shim), commands.py, io.py, menus.py, __init__.py
modules/
  shapes/lines/straight/ (parser, arrows, renderer, processor)
  shapes/lines/curve/    (parser, arrows, renderer, processor)
  shapes/ellipse/        (parser, renderer, processor)
  shapes/arc/            (arrows, renderer, processor)
  styles/colors/         (kdtree, utils, color_postprocessor)
  styles/fillings/       (opacity_postprocessor)
  styles/dashes/         (dash_postprocessor, utils)
utils/
  geometry/              (shared_arrow_logic, bezier, base_geometry, ...)
  maintenance/           (get_color.py)
```
