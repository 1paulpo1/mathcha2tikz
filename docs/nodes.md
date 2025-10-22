# Findings

- **[Objective]** Add “nodes” post-processing that:
  - Parses nodes from the raw input.
  - Collects anchor points P from rendered shapes (excluding node coords).
  - For each node N, finds nearest anchor P, computes vector P→N, maps its angle to a positioning keyword, and inserts a node command near P in the final TikZ output.

# Proposed architecture

- **[Where it lives]**
  - Parsers for nodes: `modules/nodes/node_parser.py`
  - Post-process utilities: `utils/nodes/anchors.py`, `utils/nodes/search.py`, `utils/nodes/positioning.py`, `utils/nodes/types.py`
  - Orchestration: small “nodes pass” in `core/renderer.GlobalRenderer` after shapes have been processed/rendered.

- **[Data flow]**
  1. `NodeParser` scans the original raw input once to extract nodes N and their coordinates/content (and remove them from normal shape parsing if needed).
  2. Shapes pipeline runs as today, producing a list of rendered items and per-item metadata (we already output `start_point`, `end_point`, `center`, etc.).
  3. Nodes pass:
     - Build anchors P from rendered items’ metadata (not from raw strings).
     - For each N, find nearest P via search backend, compute vector and angle.
     - Map angle to `above/below/left/right/diagonals`.
     - Create TikZ node command and insert it adjacent to the rendered item that produced P (by index).

# Step-by-step plan

- **Phase 1 — Types and utilities**
  - **`utils/nodes/types.py`**
    - `Point = Tuple[float, float]` (reuse `utils/shapes/types.Point`).
    - `ParsedNode(TypedDict)`: `id: Optional[str]`, `at: Point`, `content: str`, `styles: StyleDict`, `raw: str`.
    - `Anchor(TypedDict)`: `point: Point`, `render_index: int`, `kind: Literal['start','end','center','other']`, `shape_type: str`, `shape_id: Optional[str]`.
    - `NodePlacement(TypedDict)`: `anchor_index: int`, `node_index: int`, `position: str`, `angle: float`.
  - **`utils/nodes/search.py`**
    - Start with brute force nearest neighbor:
      - `nearest_point(points: List[Point], q: Point) -> Tuple[int, float]`
      - `nearest_many(points: List[Point], queries: List[Point]) -> List[Tuple[int, float]]`
    - Later add KDTree backend (colors’ kdtree or optional SciPy `cKDTree`) behind a strategy flag.
  - **`utils/nodes/positioning.py`**
    - `vector_angle_deg(dx, dy) -> float` returns [0, 360).
    - `angle_to_position(angle) -> str` mapping:
      - right: [-22.5, 22.5); above right: [22.5, 67.5); above: [67.5, 112.5); above left: [112.5, 157.5); left: [157.5, 202.5); below left: [202.5, 247.5); below: [247.5, 292.5); below right: [292.5, 337.5); wrap-around to right.
    - Keep thresholds configurable for tuning.

- **Phase 2 — Node parsing**
  - **`modules/nodes/node_parser.py`**
    - Parse `\node[...] at (x, y) {content};` (basic regex; include optional node name `(id)` if present).
    - Output `List[ParsedNode]`.
    - Keep raw text (e.g., for comments). If node styles present, parse via `utils/style_utils.parse_style_blocks()` into `StyleDict`.
  - Integration: Call node parser early from the overall pipeline (e.g., CLI or renderer entry), persist the `ParsedNode[]` list in the context passed to `GlobalRenderer`.

- **Phase 3 — Anchor collection**
  - **`utils/nodes/anchors.py`**
    - `collect_anchors(rendered_items: List[Dict[str, Any]]) -> List[Anchor]`
    - Use metadata we already add in processors:
      - Straight: `start_point`, `end_point`.
      - Curve: `start_point`, `end_point`.
      - Ellipse/Circle: `center`.
      - Arc: `center` or representative points if desired.
    - Store `render_index` so we can insert nodes near the correct item.
    - Exclude any points that coincide with node `at` points (by eps tolerance).

- **Phase 4 — Placement and insertion**
  - **`modules/nodes/node_placer.py`**
    - `place_nodes(nodes: List[ParsedNode], anchors: List[Anchor], search_backend='bruteforce') -> List[NodePlacement]`
    - For each node:
      - Find nearest anchor index and distance.
      - Compute vector P→N and angle, map to position via positioning utils.
      - Produce `NodePlacement`.
  - Generate TikZ node commands:
    - Format using existing number formatting (`utils/style_utils.format_number`) and style string building.
    - Example: `\node[above right] at (Px, Py) {content};`
    - Optional: if you need to preserve ID, append a comment `%% node:id`.

  - Insertion into output:
    - In `core/renderer.GlobalRenderer` after per-item rendering, splice node command right after the item at `render_index`:
      - If `rendered_items[render_index]` produces `tikz_code`, append a new line with the node command.
      - If items combine later into a single string, track insertion indices similarly (or attach `extra_lines_after` array to items and fold at the end).

- **Phase 5 — Integration & flags**
  - Add a renderer option in `context.pipeline_config['nodes']` (default off).
  - Wire `GlobalRenderer`:
    - If enabled and nodes are present:
      1. Collect anchors from `rendered_items`.
      2. Place nodes to compute insertions.
      3. Insert generated node commands adjacent to anchors.

- **Phase 6 — Backends and optimization**
  - Switch search backend from brute force to KDTree if necessary:
    - Provide `backend='kdtree'` that uses `modules/styles/colors/utils/kdtree.py` API.
    - Optionally add SciPy’s `cKDTree` if the project is ready to include SciPy (guarded import and fallback).

- **Phase 7 — Tests and metrics**
  - Unit tests:
    - NodeParser (common node syntaxes).
    - Anchors aggregation from sample rendered items (straight/curve/ellipse/arc).
    - Angle mapping thresholds.
    - Placer nearest-neighbor and position selection.
    - Insertion preserves shape order and adds correct node lines.
  - Optional CLI metrics (count nodes, average distance P→N, backend used).

# File changes summary

- **Add**
  - `utils/nodes/types.py`
  - `utils/nodes/search.py`
  - `utils/nodes/positioning.py`
  - `utils/nodes/anchors.py`
  - `modules/nodes/node_parser.py`
  - `modules/nodes/node_placer.py`

- **Modify**
  - [core/renderer.py](cci:7://file:///Users/paul/mathcha2tikz/core/renderer.py:0:0-0:0):
    - Add a post-render nodes pass (feature-gated).
  - [CLI.py](cci:7://file:///Users/paul/mathcha2tikz/CLI.py:0:0-0:0):
    - Add CLI flag `--nodes/--no-nodes` or a mode toggle to enable the pass, with basic counters in logs.

# Notes and trade-offs

- **Anchors source**: Using per-item metadata avoids brittle parsing of final TikZ strings.
- **ID handling**: Accept loss of node ID in final code for visual fidelity; optionally preserve it in a trailing comment.
- **Positioning**: Start with 8-way mapping; adding 16-way (e.g., “above slightly right”) is possible later.

# Recommended Actions

- **Start with scaffolding (Phases 1–3)**:
  - Create [types.py](cci:7://file:///Users/paul/mathcha2tikz/utils/shapes/types.py:0:0-0:0), `search.py`, `positioning.py`, `anchors.py`, and `node_parser.py`.
  - Wire parser invocation at the top-level to capture nodes list.
- **Implement placement & insertion (Phases 4–5)**:
  - Add `node_placer.py`, integrate with `GlobalRenderer`, behind a feature flag.
- **Iterate**:
  - Benchmark brute force vs KDTree when your node counts grow; switch backend as needed.
  - Add tests for stability.

# Task status

- Plan prepared with concrete module structure, interfaces, and integration points in `core/renderer.GlobalRenderer`. Ready to implement Phase 1 scaffolding on your signal.