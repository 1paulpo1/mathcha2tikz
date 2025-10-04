# TODO: This file is deprecated. Functionality will be moved to other files

"""
Formatter for TikZ code optimization and final formatting.
"""

import re
import logging
from typing import Set, Dict, Any, Optional
from utils.maintenance.optimization import coordinate_cache, batch_processor
from utils.maintenance.performance import timing_context
from utils.cache.regex_patterns import regex_patterns
from modules.styles.colors.utils.color_base import COLOR_DEFINITIONS

# Define DEFAULT_COLORS as a subset of common colors
DEFAULT_COLORS = {
    "Black", "White", "Red", "Green", "Blue", "Yellow", "Cyan", "Magenta",
    "Gray", "Grey", "Orange", "Purple", "Brown", "Pink", "Lime", "Navy",
    "Teal", "Maroon", "Olive", "Aqua", "Silver", "Gold", "Indigo", "Violet"
}

# Add a logger for regex errors
regex_logger = logging.getLogger("regex_debug")
regex_logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
handler.setLevel(logging.DEBUG)
regex_logger.addHandler(handler)

# Wrap re.sub and re.compile with logging
import re as _re

def safe_sub(pattern, repl, string, **kwargs):
    try:
        return _re.sub(pattern, repl, string, **kwargs)
    except Exception as e:
        regex_logger.error(f"Regex error in re.sub: pattern={pattern!r}, repl={repl!r}, error={e}")
        raise

def safe_compile(pattern, **kwargs):
    try:
        return _re.compile(pattern, **kwargs)
    except Exception as e:
        regex_logger.error(f"Regex error in re.compile: pattern={pattern!r}, error={e}")
        raise


def process(tikz_code: str) -> str:
    """
    Process and format TikZ code with optimizations.
    
    Args:
        tikz_code: The input TikZ code to format
        
    Returns:
        Formatted TikZ code
    """
    with timing_context("formatting"):
        # Extract and clean tikzpicture content first
        tikz_code = _extract_tikzpicture_content(tikz_code)
        
        # Clean the code
        tikz_code = _clean_tikz_code(tikz_code)
        
        # Use centralized processing pipeline
        from utils.maintenance.maintenance_manager import conversion_pipeline
        tikz_code, _ = conversion_pipeline.convert(tikz_code)
        
        # Apply arc conversion to the entire processed code (if available)
        try:
            from utils.geometry.conics.conic_arc import main as detect_and_convert_similar_radius_arcs
            tikz_code = detect_and_convert_similar_radius_arcs(tikz_code)
        except ImportError:
            pass  # Arc conversion not available
        
        # Apply robust formatting for consistency
        tikz_code = format_consistently(tikz_code)
        
        return tikz_code


def format_consistently(tikz_code: str) -> str:
    """
    Apply all formatting consistently for robust output.
    
    Args:
        tikz_code: Input TikZ code
        
    Returns:
        Consistently formatted TikZ code
    """
    try:
        # Apply formatting steps in order
        result = tikz_code
        
        # Step 1: Handle specific formatting issues first
        result = handle_specific_formatting_issues(result)
        
        # Step 2: Normalize whitespace
        result = normalize_whitespace(result)
        
        # Step 3: Format draw commands
        result = format_draw_commands(result)
        
        # Step 4: Format comments
        result = format_comments(result)
        
        # Step 5: Normalize newlines
        result = normalize_newlines(result)
        
        # Step 6: Format environment
        result = format_environment(result)
        
        return result
        
    except Exception as e:
        print(f"Error in robust formatting: {e}")
        return tikz_code


def handle_specific_formatting_issues(tikz_code: str) -> str:
    """
    Handle specific formatting issues that cause test failures.
    
    Args:
        tikz_code: Input TikZ code
        
    Returns:
        TikZ code with specific issues fixed
    """
    # Fix the specific issue with comment and draw command on same line
    tikz_code = re.sub(r'(%[^\\]*?)\\draw', r'\1\n\\draw', tikz_code)
    
    # Fix spacing around tikzpicture environment
    tikz_code = re.sub(r'\\begin\{tikzpicture\}\s*\[([^\]]+)\]', r'\\begin{tikzpicture}[\1]', tikz_code)
    
    # Ensure proper spacing after comments
    tikz_code = re.sub(r'(%[^\n]*)\n(\\draw)', r'\1\n\n\2', tikz_code)
    
    # Normalize comment formatting
    tikz_code = re.sub(r'%([^ ])', r'% \1', tikz_code)
    
    return tikz_code


def normalize_whitespace(tikz_code: str) -> str:
    """
    Normalize whitespace in TikZ code.
    
    Args:
        tikz_code: Input TikZ code
        
    Returns:
        Normalized TikZ code
    """
    # Remove excessive whitespace while preserving structure
    lines = tikz_code.split('\n')
    normalized_lines = []
    
    for line in lines:
        # Strip leading/trailing whitespace
        line = line.strip()
        
        # Skip empty lines
        if not line:
            continue
            
        # Normalize internal whitespace for TikZ commands
        if line.startswith('\\'):
            # For TikZ commands, normalize spacing
            line = re.sub(r'\s+', ' ', line)
            # Ensure proper spacing around brackets
            line = re.sub(r'\[([^\]]*)\]', r'[\1]', line)
            line = re.sub(r'\{([^}]*)\}', r'{\1}', line)
        else:
            # For comments and other content, preserve structure
            line = re.sub(r'\s+', ' ', line)
        
        normalized_lines.append(line)
    
    return '\n'.join(normalized_lines)


def format_draw_commands(tikz_code: str) -> str:
    """
    Format draw commands consistently.
    
    Args:
        tikz_code: Input TikZ code
        
    Returns:
        Formatted TikZ code
    """
    lines = tikz_code.split('\n')
    formatted_lines = []
    
    for line in lines:
        if line.strip().startswith('\\draw'):
            # Format draw commands consistently
            formatted_line = _format_draw_command(line)
            formatted_lines.append(formatted_line)
        else:
            formatted_lines.append(line)
    
    return '\n'.join(formatted_lines)


def _format_draw_command(line: str) -> str:
    """
    Format a single draw command.
    
    Args:
        line: Draw command line
        
    Returns:
        Formatted draw command
    """
    # Extract components
    match = re.match(r'\\draw\s*(\[.*?\])?\s*(.*)', line)
    if not match:
        return line
    
    style_part = match.group(1) or ''
    path_part = match.group(2).strip()
    
    # Format the command
    if style_part:
        # Ensure proper spacing around style brackets
        style_part = style_part.strip()
        formatted_line = f"\\draw{style_part} {path_part}"
    else:
        formatted_line = f"\\draw {path_part}"
    
    return formatted_line


def normalize_newlines(tikz_code: str) -> str:
    """
    Normalize newlines in TikZ code.
    
    Args:
        tikz_code: Input TikZ code
        
    Returns:
        TikZ code with normalized newlines
    """
    # Split into lines and remove empty lines
    lines = [line.strip() for line in tikz_code.split('\n') if line.strip()]
    
    # Add proper spacing between sections
    formatted_lines = []
    for i, line in enumerate(lines):
        formatted_lines.append(line)
        
        # Add newline after comments if next line is a draw command
        if line.startswith('%') and i + 1 < len(lines):
            next_line = lines[i + 1]
            if next_line.startswith('\\draw'):
                formatted_lines.append('')
    
    return '\n'.join(formatted_lines)


def format_comments(tikz_code: str) -> str:
    """
    Format comments consistently.
    
    Args:
        tikz_code: Input TikZ code
        
    Returns:
        TikZ code with formatted comments
    """
    lines = tikz_code.split('\n')
    formatted_lines = []
    
    for line in lines:
        if line.strip().startswith('%'):
            # Ensure consistent comment formatting
            comment = line.strip()
            if not comment.startswith('% '):
                comment = comment.replace('%', '% ', 1)
            formatted_lines.append(comment)
        else:
            formatted_lines.append(line)
    
    return '\n'.join(formatted_lines)


def format_environment(tikz_code: str) -> str:
    """
    Format TikZ environment consistently.
    
    Args:
        tikz_code: Input TikZ code
        
    Returns:
        Formatted TikZ code
    """
    # Ensure proper spacing in tikzpicture environment
    tikz_code = re.sub(r'\\begin\{tikzpicture\}\s*\[', r'\\begin{tikzpicture}[\n', tikz_code)
    tikz_code = re.sub(r'\]\s*\\end\{tikzpicture\}', r'\n]\\end{tikzpicture}', tikz_code)
    
    return tikz_code


def compare_formatted(actual: str, expected: str) -> bool:
    """
    Compare two TikZ strings with normalized formatting.
    
    Args:
        actual: Actual output
        expected: Expected output
        
    Returns:
        True if they match after formatting normalization
    """
    actual_formatted = format_consistently(actual)
    expected_formatted = format_consistently(expected)
    
    return actual_formatted == expected_formatted


def _remove_default_color_definitions(tikz_code: str) -> str:
    """Remove default color definitions that are already available in TikZ or are core colors."""
    
    # Convert DEFAULT_COLORS to lowercase for case-insensitive comparison
    default_colors_lower = {color.lower() for color in DEFAULT_COLORS}
    
    # Pattern to match color definitions
    color_def_pattern = re.compile(r'\\definecolor\{([^}]+)\}\{rgb\}\{([^}]+)\}', re.IGNORECASE)
    
    def should_remove_color(match):
        color_name = match.group(1).lower()
        
        # Simple if statement approach: if color name matches any default color, remove it
        if color_name in default_colors_lower:
            return ''
        
        return match.group(0)
    
    tikz_code = color_def_pattern.sub(should_remove_color, tikz_code)
    tikz_code = re.sub(r'\n\s*\n\s*\n', '\n\n', tikz_code)
    return tikz_code


def _apply_optimizations(line: str, optimizations: list) -> str:
    """Apply all optimizations to a single line."""
    result = line
    for optimization in optimizations:
        result = optimization(result)
    return result


def _remove_opacity_one(tikz_code: str) -> str:
    """Remove draw opacity=1 and fill opacity=1."""
    # More comprehensive opacity removal
    patterns = [
        r'(?:draw|fill) opacity\s*=\s*1(,)?\s*',
        r'opacity\s*=\s*1(,)?\s*',
    ]
    for pattern in patterns:
        tikz_code = safe_sub(pattern, '', tikz_code)
    # Clean up any trailing commas left after removing opacity
    tikz_code = safe_sub(r',\s*]', ']', tikz_code)
    return tikz_code


def _remove_duplicate_dash_patterns(tikz_code: str) -> str:
    """Remove duplicate dash patterns in the same style group."""
    # Find style groups with duplicate dash patterns
    def replace_duplicates(match):
        style_content = match.group(1)
        try:
            parts = _re.split(r'(dash pattern\s*=\s*\{[^}]+\})', style_content)
        except Exception as e:
            raise
        unique_parts = []
        seen_dash_patterns = set()
        
        for part in parts:
            if part.strip().startswith('dash pattern'):
                if part not in seen_dash_patterns:
                    seen_dash_patterns.add(part)
                    unique_parts.append(part)
            else:
                unique_parts.append(part)
        
        return '[' + ''.join(unique_parts) + ']'
    
    # Apply to style groups - use safe_sub to avoid escape issues
    tikz_code = safe_sub(r'\[([^]]*)\]', replace_duplicates, tikz_code)
    return tikz_code


def _merge_style_groups(tikz_code: str) -> str:
    """Merge multiple consecutive style groups into a single bracketed group, flattening all contents."""
    # Find all style groups and flatten their contents
    def merge_groups(match):
        groups = match.groups()
        # Remove brackets and split by comma
        contents = []
        for g in groups:
            if g:
                inner = g.strip()[1:-1]  # remove [ and ]
                if inner:
                    contents.append(inner)
        # Join all contents with comma and wrap in single brackets
        return '[' + ', '.join(contents) + ']'
    # Replace all consecutive style groups
    while re.search(r'(\[[^]]*\])(?:\s*(\[[^]]*\])\s*)+', tikz_code):
        tikz_code = safe_sub(r'(\[[^]]*\])(?:\s*(\[[^]]*\])\s*)+', merge_groups, tikz_code)
    return tikz_code


def _indent_path_continuations(tikz_code: str) -> str:
    """Indent all path continuation lines (.., --, arc) with 4 spaces."""
    lines = tikz_code.split('\n')
    result = []
    for i, line in enumerate(lines):
        if i > 0 and (line.lstrip().startswith('..') or line.lstrip().startswith('--') or line.lstrip().startswith('arc')):
            result.append('    ' + line.lstrip())
        else:
            result.append(line)
    return '\n'.join(result)


def _indent_decoration_marks(tikz_code: str) -> str:
    """Indent every 'mark=at position' line inside a 'decoration={markings, ...}' block with 4 spaces."""
    # Regex to match the decoration block
    pattern = re.compile(r'(decoration=\{markings,\s*)(.*?)(\}, postaction=\{decorate\})', re.DOTALL)
    def replacer(match):
        start, body, end = match.groups()
        # Indent every 'mark=at position' line
        body = re.sub(r'(^|\n)(\s*mark=at position)', r'\1    mark=at position', body)
        return start + body + end
    return pattern.sub(replacer, tikz_code)


def _clean_coordinates(tikz_code: str) -> str:
    """Clean coordinate formatting using coordinate cache."""
    # Use coordinate cache for coordinate strings
    def clean_coord(match):
        coord_str = match.group(0)
        return coordinate_cache.normalize_coordinate(coord_str)
    # Apply coordinate cleaning patterns
    coord_patterns = [
        (r'\(\s*', '('),
        (r'\s*\)', ')'),
        (r'\s*,\s*', ', '),
        (r',\s*\]', ']'),
    ]
    for pattern, replacement in coord_patterns:
        try:
            tikz_code = safe_sub(pattern, replacement, tikz_code)
        except Exception as e:
            raise
    return tikz_code


def _remove_empty_brackets(tikz_code: str) -> str:
    """Remove empty draw brackets."""
    try:
        result = safe_sub(r'^\s*\\draw\[\s*\]', r'\\draw', tikz_code)
        return result
    except Exception as e:
        raise


def _remove_fractional_zeros(tikz_code: str) -> str:
    """Remove .0 from integer numbers."""
    return safe_sub(r'(\d+)\.0+(?=\D)', r'\1', tikz_code)


def _remove_double_commas(tikz_code: str) -> str:
    """Remove double commas."""
    return safe_sub(r',\s*,', ',', tikz_code)


def _remove_backslash_equals(tikz_code: str) -> str:
    """Remove backslash equals."""
    return safe_sub(r"\\\s*=\s*", '=', tikz_code)


def _remove_leading_commas(tikz_code: str) -> str:
    """Remove leading commas in brackets."""
    return safe_sub(r'\[\s*,\s*', '[', tikz_code)


def _remove_duplicate_styles(tikz_code: str) -> str:
    """Remove duplicate style names."""
    return safe_sub(r'(\b\w+\b)(?:\s*,\s*\1\b)+', r'\1', tikz_code)


def _comment_section_headers(line: str) -> str:
    """Ensure Mathcha section headers are commented out with a % at the start of the line."""
    # Matches lines like 'Straight Lines [id:...]', 'Curve Lines [id:...]', 'Shape: ...', etc.
    if re.match(r'^(Straight Lines|Curve Lines|Shape:|Nodes:|Arrows:|Polygon Curved|Ellipse|Circle|Arc|Polygon|Rectangle|Text|Image|Node) ', line):
        return '%' + line if not line.strip().startswith('%') else line
    return line


def _extract_tikzpicture_content(tikz_code: str) -> str:
    """
    Extract and clean the content of tikzpicture environment.
    
    Args:
        tikz_code: Raw Mathcha TikZ code
        
    Returns:
        Cleaned tikzpicture content
    """
    # Find start and end of tikzpicture environment
    start_match = re.search(r'\\begin\{tikzpicture\}.*?\n', tikz_code, re.DOTALL)
    end_match = re.search(r'\\end\{tikzpicture\}', tikz_code, re.DOTALL)
    
    if not start_match or not end_match:
        return tikz_code  # Return as-is if not found
        
    start_index = start_match.end()
    end_index = end_match.start()
    
    # Extract content between \begin{tikzpicture} and \end{tikzpicture}
    content = tikz_code[start_index:end_index].strip()
    
    # Remove "uncomment if require" comment
    content = safe_sub(r'%uncomment if require:.*\n', '', content)
    # Remove empty lines
    content = safe_sub(r'\n\s*\n', '\n', content).strip()
    # Remove empty text nodes
    content = safe_sub(r'%uncomment if require:.*\n', '', content)
    
    return content


def _clean_tikz_code(tikz_code: str) -> str:
    """
    Clean TikZ code by removing any existing preamble elements.
    
    Args:
        tikz_code: The TikZ code to clean
        
    Returns:
        Cleaned TikZ code with only the drawing commands
    """
    # Remove any existing preamble elements that might be duplicated
    patterns_to_remove = [
        r'\\usetikzlibrary\{[^}]*\}',
        r'\\tikzset\{[^}]*\}',
        r'\\definecolor\{[^}]*\}',
        r'\\begin\{document\}',
        r'\\end\{document\}',
    ]
    for pattern in patterns_to_remove:
        tikz_code = safe_sub(pattern, '', tikz_code, flags=re.DOTALL)
    
    # Clean up extra whitespace and empty lines
    lines = tikz_code.split('\n')
    cleaned_lines = []
    for line in lines:
        line = line.strip()
        if line:  # Keep non-empty lines
            cleaned_lines.append(line)
    
    return '\n'.join(cleaned_lines)


def build_doc(tikz_code: str, used_colors: Set[str], dash_styles_dict: Optional[Dict[str, str]] = None) -> str:
    """
    Build the complete TikZ document with preamble and color definitions.
    
    Args:
        tikz_code: The processed TikZ code
        used_colors: Set of colors used in the document
        dash_styles_dict: Dictionary of dash styles to include
        
    Returns:
        Complete TikZ document
    """
    with timing_context("document_building"):
        # Build preamble
        preamble = _build_preamble(used_colors, dash_styles_dict)
        
        # Always include 'line width = 0.75pt' in tikzpicture options
        tikzpicture_options = "x = 0.75pt, y = 0.75pt, yscale = -1"
        if "line width" not in tikzpicture_options:
            tikzpicture_options += ", line width = 0.75pt"
        doc = f"""{preamble}\n\n\\begin{{document}}\n\\begin{{tikzpicture}}[{tikzpicture_options}]
        \n{tikz_code}\n\\end{{tikzpicture}}\n\\end{{document}}"""
        
        return doc


def _remove_existing_environments(tikz_code: str) -> str:
    """Extract content from existing document/tikzpicture environments without losing drawing commands."""
    # 1. If a full document environment is present, keep only its body
    doc_match = re.search(r'\\begin\{document\}(.*?)\\end\{document\}', tikz_code, re.DOTALL)
    if doc_match:
        tikz_code = doc_match.group(1)

    # 2. Extract content from tikzpicture environment if present
    start_match = re.search(r'\\begin\{tikzpicture\}(?:\[[^]]*\])?\s*\n?', tikz_code, re.DOTALL)
    end_match = re.search(r'\\end\{tikzpicture\}', tikz_code, re.DOTALL)
    if start_match and end_match:
        tikz_code = tikz_code[start_match.end():end_match.start()].strip()

    # 3. Remove the default line width comment inserted by Mathcha
    tikz_code = safe_sub(r'}\s*%set default line width to 0\.75pt\s*\n?', '', tikz_code, flags=re.DOTALL)

    # 4. Collapse multiple blank lines
    tikz_code = safe_sub(r'\n\s*\n', '\n', tikz_code)
    return tikz_code.strip()


def _build_preamble(used_colors: Set[str], dash_styles_dict: Optional[Dict[str, str]] = None) -> str:
    """
    Build the document preamble with libraries, settings, and color definitions.
    
    Args:
        used_colors: Set of colors used in the document
        dash_styles_dict: Dictionary of dash styles to include
        
    Returns:
        Document preamble
    """
    preamble_parts = []
    
    # Add TikZ libraries
    preamble_parts.append("\\usetikzlibrary{arrows.meta, decorations.markings, bending}")
    
    # Add TikZ settings
    preamble_parts.append("\\tikzset{>={Stealth[length=6pt, width=4pt, bend]}}")
    
    # Add color definitions
    for color_name in sorted(used_colors):
        color_def = _get_color_definition(color_name)
        if color_def:
            preamble_parts.append(color_def)
    
    # Add dash style definitions
    if dash_styles_dict:
        dash_tikzset = _build_dash_tikzset(dash_styles_dict)
        if dash_tikzset:
            preamble_parts.append(dash_tikzset)
    
    return '\n'.join(preamble_parts)


def _get_color_definition(color_name: str) -> str:
    """
    Get the color definition for a given color name.
    
    Args:
        color_name: Name of the color
        
    Returns:
        Color definition string or empty string if not found
    """
    # Import here to avoid circular imports
    
    # Check if this is a default color - if so, don't include the definition
    if color_name.lower() in {color.lower() for color in DEFAULT_COLORS}:
        return ""
    
    if color_name in COLOR_DEFINITIONS:
        return COLOR_DEFINITIONS[color_name]
    return ""


def _build_dash_tikzset(dash_styles_dict: Dict[str, str]) -> str:
    """
    Build TikZ settings for dash styles.
    
    Args:
        dash_styles_dict: Dictionary of dash styles
        
    Returns:
        TikZ settings string
    """
    if not dash_styles_dict:
        return ""
    
    dash_definitions = []
    for style_name, pattern in dash_styles_dict.items():
        dash_definitions.append(f"{style_name}/.style={{dash pattern={{{pattern}}}}}")
    
    return f"\\tikzset{{{', '.join(dash_definitions)}}}"