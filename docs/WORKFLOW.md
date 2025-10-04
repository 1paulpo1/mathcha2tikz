# mathcha2tikz Workflow and Architecture
 
 This document describes the current conversion pipeline, key modules, and extensibility points as of Oct 2025.

## High-level Pipeline

 1. **Input acquisition**
    - CLI entry: `python -m mathcha2tikz.cli` (preferred) or `python mathcha2tikz/cli.py`
    - Python API: `core.converter.Converter` (preferred) or `core.main.convert()`
    - Clipboard/editor/stdin helpers live in `mathcha2tikz/cli_io.py`
    - Converter bootstrap calls `ensure_builtin_processors_registered()` and `ensure_builtin_renderers_registered()` to lazily configure registries (no heavy imports at module import time)

2. **Detection & Parsing**
   - Shapes are detected and dispatched to specialized parsers
   - Current shape coverage:
     - `Straight Lines`: `modules/shapes/lines/straight/straight_parser.py`
     - `Curve Lines`: `modules/shapes/lines/curve/curve_parser.py`
     - `Ellipse/Circle`: `modules/shapes/ellipse/ellipse_parser.py`
     - `Arc`: `modules/shapes/arc/arc_parser.py`
   - Parsers extract:
     - Main drawable command (exclude arrow-only helpers and invisible draws)
     - Inline styles into a dict (e.g. `color`, `opacity`, `dash pattern`)
     - Arrow auxiliary commands (shift/rotate blocks) for arrows processing

3. **Processing**
   - Each shape has a processor that merges parser data and arrow info
   - Processor lookup goes through `core/processor.ProcessorRegistry`, populated lazily via `ensure_builtin_processors_registered()`
   - Key processors:
     - `StraightProcessor`: `modules/shapes/lines/straight/straight_processor.py`
     - `CurveProcessor`: `modules/shapes/lines/curve/curve_processor.py`
     - `EllipseProcessor`: `modules/shapes/ellipse/ellipse_processor.py`
     - `ArcProcessor`: `modules/shapes/arc/arc_processor.py`
   - Responsibilities:
     - Normalize/merge styles into dict
     - Process arrows (start/end/mid) and compute geometry where needed

4. **Rendering**
   - Renderers build final TikZ commands
   - `GlobalRenderer` normalizes render payloads (type/id/styles) before delegating to shape renderers
   - Renderers are registered lazily through `ensure_builtin_renderers_registered()` in `core/renderer.py`
   - Renderers prefer assembling styles from dicts (consistent with `Arc/Ellipse`), or merge dict into style string when required:
     - `modules/shapes/lines/straight/straight_renderer.py`
     - `modules/shapes/lines/curve/curve_renderer.py`
     - `modules/shapes/ellipse/ellipse_renderer.py`
     - `modules/shapes/arc/arc_renderer.py`

5. **Output composition**
    - `core/renderer.py` concatenates rendered parts, raises `RenderingError` on failures, and applies output mode template via `core/templates.py` (immutable `TEMPLATES` map):
      - `classic`: commented preamble hints with minimal post-processing (trailing newline normalization)
      - `obsidian` (default): active `\usetikzlibrary`/`\tikzset` and `\begin{document}` wrapper

6. **Post-processing**
   - `ColorPostProcessor`: expands color definitions and injects color table
   - `OpacityPostProcessor`: removes redundant `draw opacity=1` and preserves others
   - `DashPatternPostProcessor`: de-duplicates, normalizes, and converts dash patterns by dictionary
     - Module: `modules/styles/dashes/dash_postprocessor.py`
     - Uses `DASH_PATTERNS` from `modules/styles/dashes/dash_builder.py` for exact-name conversion
   - Order in `core/main.py`:
     1. Render to TikZ by mode
     2. Color post-process
     3. Opacity post-process
     4. Dash post-process (normalize/dedupe/convert)
     5. Reconstruct final output (preamble + tikzpicture for classic; document wrapper for obsidian)

## Typing and payload contracts
 
 - Shape payload flowing Detector → Processor → Renderer conforms to `core/shape_payload.py` `ShapePayload` Protocol.
   - Minimal attributes: `id`, `shape_type`, `annotation`, `raw_block`, `raw_command`, optional `raw_shape_data`, `raw_arrows_data`.
   - Processors accept `shape_instance: Optional[ShapePayload]` and still use `getattr()` for robustness.
 - Per-processor input dataclasses (e.g., `StraightInput`, `CurveInput`, `ArcInput`, `EllipseInput`) document expected attributes without changing runtime behavior.
 - Arrow typing unified:
   - Straight: `StraightArrowInfo` and `StraightMidArrow` (`ArrowDirection = Literal['<','>']`).
   - Curve/Arc: `TypedDict` payloads with explicit fields; directions aligned to `ArrowDirection`.
 
## CLI layout
 
 - `mathcha2tikz/cli.py`: thin entrypoint (argparse, logging, context wiring) with Obsidian as default mode.
 - `mathcha2tikz/commands.py`: `run_conversion()`, `quick_convert()`.
 - `mathcha2tikz/cli_io.py`: stdin/clipboard/editor helpers.
 - `mathcha2tikz/cli_menus.py`: interactive menus; only core items are exposed now:
   - Settings: Render Mode, Input Method (module toggles and pipeline configuration hidden).
   - Debug: Global debug toggle (per-module debug UI hidden).
 
## Tests

- E2E tests for both modes (classic, obsidian)
- Unit tests for post-processors: dash normalization, deduplication, exact-name conversion
