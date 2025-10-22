# Findings (code duplication hot-spots)

- **[Renderers share the same helpers]**
  - Files: [modules/shapes/lines/straight/straight_renderer.py](cci:7://file:///Users/paul/mathcha2tikz/modules/shapes/lines/straight/straight_renderer.py:0:0-0:0), [modules/shapes/lines/curve/curve_renderer.py](cci:7://file:///Users/paul/mathcha2tikz/modules/shapes/lines/curve/curve_renderer.py:0:0-0:0), [modules/shapes/arc/arc_renderer.py](cci:7://file:///Users/paul/mathcha2tikz/modules/shapes/arc/arc_renderer.py:0:0-0:0), [modules/shapes/ellipse/ellipse_renderer.py](cci:7://file:///Users/paul/mathcha2tikz/modules/shapes/ellipse/ellipse_renderer.py:0:0-0:0)
  - Repeats:
    - [_fmt_num()](cci:1://file:///Users/paul/mathcha2tikz/modules/shapes/arc/arc_renderer.py:14:4-15:35) using `utils.style_utils.format_number`
    - [_style_from_dict()](cci:1://file:///Users/paul/mathcha2tikz/modules/shapes/arc/arc_renderer.py:17:4-18:55) using `style_dict_to_str`
    - Coordinate/point formatting and string assembly for `\draw ...`
    - ID header via `utils.id_utils.build_id_header(...)`
    - Arrow applying via `utils.style_utils.apply_arrow_styles(...)`
    - Raw passthrough checks for `processed['raw']` or `processed['tikz_code']`

- **[Path/coordinate string building]**
  - Files: [straight_renderer.py](cci:7://file:///Users/paul/mathcha2tikz/modules/shapes/lines/straight/straight_renderer.py:0:0-0:0), [curve_renderer.py](cci:7://file:///Users/paul/mathcha2tikz/modules/shapes/lines/curve/curve_renderer.py:0:0-0:0)
  - Repeats:
    - Line coordinates builder (start/end formatting)
    - Curve path builder (segments → “.. controls … and … ..” + optional `-- cycle`)

- **[Parsers – same structure and style extraction]**
  - Files: [modules/shapes/arc/arc_parser.py](cci:7://file:///Users/paul/mathcha2tikz/modules/shapes/arc/arc_parser.py:0:0-0:0), [modules/shapes/ellipse/ellipse_parser.py](cci:7://file:///Users/paul/mathcha2tikz/modules/shapes/ellipse/ellipse_parser.py:0:0-0:0), [modules/shapes/lines/curve/curve_parser.py](cci:7://file:///Users/paul/mathcha2tikz/modules/shapes/lines/curve/curve_parser.py:0:0-0:0), [modules/shapes/lines/straight/straight_parser.py](cci:7://file:///Users/paul/mathcha2tikz/modules/shapes/lines/straight/straight_parser.py:0:0-0:0)
  - Repeats:
    - Split or iterate “\draw …” lines
    - Select main command (has bezier controls / not opacity=0 / not shift/rotate)
    - Collect arrow/aux lines (contain `shift`, `rotate`, sometimes `cycle`)
    - Extract styles with `STYLE_BLOCK_PATTERN` and `parse_style_blocks`

- **[Processors – similar workflow]**
  - Files: [modules/shapes/ellipse/ellipse_processor.py](cci:7://file:///Users/paul/mathcha2tikz/modules/shapes/ellipse/ellipse_processor.py:0:0-0:0), [modules/shapes/arc/arc_processor.py](cci:7://file:///Users/paul/mathcha2tikz/modules/shapes/arc/arc_processor.py:0:0-0:0) (+ straight/curve counterparts)
  - Repeats:
    - Obtain main command → parse points → split segments
    - Prepare arrows payload and normalize
    - Build processed dict with `id`, `styles`, and shape-specific fields
    - Defensive fallbacks (return raw/passthrough when inputs are insufficient)

- **[Arrows handling]**
  - Files: [modules/shapes/lines/straight/straight_arrows.py](cci:7://file:///Users/paul/mathcha2tikz/modules/shapes/lines/straight/straight_arrows.py:0:0-0:0), [modules/shapes/lines/curve/curve_arrows.py](cci:7://file:///Users/paul/mathcha2tikz/modules/shapes/lines/curve/curve_arrows.py:0:0-0:0), [modules/shapes/arc/arc_arrows.py](cci:7://file:///Users/paul/mathcha2tikz/modules/shapes/arc/arc_arrows.py:0:0-0:0), [utils/geometry/shared_arrow_logic.py](cci:7://file:///Users/paul/mathcha2tikz/utils/geometry/shared_arrow_logic.py:0:0-0:0), [utils/geometry/arrows_processor.py](cci:7://file:///Users/paul/mathcha2tikz/utils/geometry/arrows_processor.py:0:0-0:0)
  - Repeats:
    - Position classification (start/end/mid)
    - Direction/type computation from tangent vs rotation
    - Slightly different data shapes for arrow info per shape

- **[Stray duplicates to remove]**
  - Files under [utils/](cci:7://file:///Users/paul/mathcha2tikz/utils:0:0-0:0) with “copy.py” duplicates (e.g., [utils/geometry/shared_arrow_logic copy.py](cci:7://file:///Users/paul/mathcha2tikz/utils/geometry/shared_arrow_logic%20copy.py:0:0-0:0), [utils/id_utils copy.py](cci:7://file:///Users/paul/mathcha2tikz/utils/id_utils%20copy.py:0:0-0:0), [utils/style_utils copy.py](cci:7://file:///Users/paul/mathcha2tikz/utils/style_utils%20copy.py:0:0-0:0))

# DRY refactor plan (incremental, low-risk)

- **[Base renderer]**
  - New: `utils/rendering/base_renderer.py`
  - Provides shared helpers:
    - `fmt_num()`, `fmt_coord()`, `fmt_point()`
    - `style_from_dict()`
    - `apply_arrows(style_str, arrows_info)` with normalized shape-agnostic type
    - `id_header(shape_label, shape_id, raw)`
    - `passthrough_if_raw(processed)`
  - Benefit: remove per-renderer boilerplate and unify behavior.

- **[Path builder utilities]**
  - New: `utils/rendering/path_builder.py`
  - Functions:
    - `build_line_coords(start, end)` → `"(x1, y1) -- (x2, y2)"`
    - `build_curve_path(segments, is_closed)` → bezier path string (with `-- cycle`)
  - Benefit: single source for path string formatting.

- **[Parser utilities]**
  - New: `utils/parsing/parser_utils.py`
  - Functions:
    - `iter_draw_commands(raw_block)` (split multiple `\draw` in a line)
    - `is_arrow_line(s)` (shift/rotate tokens)
    - `choose_main_draw(draws, *, require_bezier=None, require_closed=None, exclude_opacity_zero=True)`
    - `extract_styles(line)` → dict via `STYLE_BLOCK_PATTERN` and `parse_style_blocks`
    - A convenience `parse_shape_common(raw_block, rules)` → `(main, arrow_cmds, styles)`
  - Benefit: collapse repeated parser logic across arc/ellipse/curve/straight.

- **[Arrow info typing + normalization]**
  - New: `utils/arrows/types.py` (TypedDict/Protocol for `ArrowsInfo`):
    - `{ start_arrow: Optional[str], end_arrow: Optional[str], mid_arrows: List[{position: float, direction: str}] }`
  - New: `utils/arrows/normalize.py` to convert shape-specific arrow results → `ArrowsInfo`
  - Update: `utils/style_utils.apply_arrow_styles` to accept `ArrowsInfo`
  - Benefit: one standard arrow structure → simpler renderers and consistent styling.

- **[Optional processor helpers]**
  - New: `core/processor_utils.py`:
    - `read_raw_block(shape_instance)` with fallback to `raw_command`
    - `append_annotation(raw_block, annotation)` if needed
  - Benefit: reduce boilerplate in each processor.

- **[Housekeeping]**
  - Remove duplicated “copy.py” shims in [utils/](cci:7://file:///Users/paul/mathcha2tikz/utils:0:0-0:0)
  - Keep only one authoritative [shared_arrow_logic.py](cci:7://file:///Users/paul/mathcha2tikz/utils/geometry/shared_arrow_logic.py:0:0-0:0)

# Proposed execution order

1) Create `BaseRenderer` and migrate one renderer (e.g., [straight_renderer.py](cci:7://file:///Users/paul/mathcha2tikz/modules/shapes/lines/straight/straight_renderer.py:0:0-0:0)) to validate API.  
2) Add `path_builder.py` and employ it in straight + curve renderers.  
3) Add `parser_utils.py` and refactor [arc_parser.py](cci:7://file:///Users/paul/mathcha2tikz/modules/shapes/arc/arc_parser.py:0:0-0:0) first (it already splits multi-draw lines).  
4) Introduce `ArrowsInfo` + normalization and update `apply_arrow_styles`, then adapt renderers.  
5) Remove duplicate “copy” files.  
6) Add unit tests for the new utilities.

# Current TODOs

- **Completed**
  - Audit duplicates and outline plan.
- **Planned (high priority)**
  - BaseRenderer and refactor renderers.
  - Parser utilities consolidation.
  - Arrow info normalization and styling.
- The full task list is tracked; I’ll mark items done as we proceed.

# Next step

Would you like me to start with:
- Implementing `utils/rendering/base_renderer.py` and migrating [straight_renderer.py](cci:7://file:///Users/paul/mathcha2tikz/modules/shapes/lines/straight/straight_renderer.py:0:0-0:0) first,
- Or begin with `utils/parsing/parser_utils.py` and refactor [arc_parser.py](cci:7://file:///Users/paul/mathcha2tikz/modules/shapes/arc/arc_parser.py:0:0-0:0)?

Both are independent; the base renderer migration yields immediate code reduction across renderers.