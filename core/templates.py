"""
Rendering templates for different output modes (Classic, Obsidian, etc.).

This module provides templates and utilities for different output modes.
"""
from typing import Dict, Any, Callable, cast


TemplateDict = Dict[str, Any]


def _classic_post_process(content: str) -> str:
    """Normalize classic output without stripping internal blank lines."""

    return content.rstrip() + "\n"


def _obsidian_post_process(content: str) -> str:
    return (
        "% Setup\n"
        "\\usetikzlibrary{arrows.meta, decorations.markings, bending}\n"
        "\\tikzset{>={Stealth[length=6pt, width=4pt, bend]}}\n\n"
        "\\begin{document}\n"
        f"{content}\n"
        "\\end{document}"
    )


TEMPLATES: Dict[str, TemplateDict] = {
    "classic": {
        "preamble": [
            "% copy to preamble",
            "% \\usetikzlibrary{arrows.meta, decorations.markings, bending}",
            "% \\tikzset{>={Stealth[length=6pt, width=4pt, bend]}}",
            "% Classic Mode - Optimized TikZ Output",
            "",
        ],
        "post_processing": cast(Callable[[str], str], _classic_post_process),
    },
    "obsidian": {
        "preamble": [""],
        "post_processing": cast(Callable[[str], str], _obsidian_post_process),
    },
}


def get_template(mode: str = 'classic') -> Dict[str, Any]:
    """
    Get the template for the specified output mode.
    
    Args:
        mode: The output mode ('classic' or 'obsidian')
        
    Returns:
        Dictionary containing template components
    """
    return TEMPLATES.get(mode.lower(), TEMPLATES['classic']).copy()


def apply_template(tikz_code: str, mode: str = 'classic') -> str:
    """
    Apply the specified template to the TikZ code.
    
    Args:
        tikz_code: The generated TikZ code
        mode: The output mode ('classic' or 'obsidian')
        
    Returns:
        Formatted TikZ code with template applied
    """
    template = get_template(mode)

    # Start with the preamble
    lines = list(template['preamble'])
    
    # Add the tikzpicture environment if not already present
    if '\\begin{tikzpicture}' not in tikz_code:
        lines.append('\\begin{tikzpicture}[x = 0.75pt, y = 0.75pt, yscale = -1, line width = 0.75pt]')
        lines.append(tikz_code)
        lines.append('\n\\end{tikzpicture}\n')
    else:
        lines.append(tikz_code)
    
    # Join lines and apply post-processing
    result = '\n'.join(lines)
    post_processing: Callable[[str], str] = template['post_processing']
    if post_processing:
        result = post_processing(result)

    return result
