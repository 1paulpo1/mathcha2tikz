# core/parser.py
"""
Parser module for converting raw Mathcha TikZ input into structured data.
"""

import re
import logging
from dataclasses import dataclass
from typing import List, Optional, Tuple

from .exceptions import ParserError

logger = logging.getLogger(__name__)

@dataclass
class ShapeBlock:
    """Represents a parsed block of TikZ code with metadata."""
    raw_block: str
    annotation: Optional[str] = None
    shape_type: Optional[str] = None
    shape_id: Optional[str] = None
    raw_shape_data: Optional[str] = None
    raw_arrows_data: Optional[str] = None


class Parser:
    """
    Parser for Mathcha TikZ code.
    Converts raw TikZ code into structured ShapeBlock objects.
    """
    
    def __init__(self):
        """Initialize the parser with default settings."""
        self.supported_shape_types = [
            'Arc', 'Straight Lines', 'Curve Lines', 'Circle',
            'Ellipse', 'Text Node', 'Node'
        ]
    
    def parse(self, input_str: str) -> List[ShapeBlock]:
        """
        Parse the input string into ShapeBlock objects.
        
        Args:
            input_str: Raw TikZ code to parse
            
        Returns:
            List of parsed ShapeBlock objects
            
        Raises:
            ParserError: If parsing fails
        """
        if not input_str or not isinstance(input_str, str):
            raise ParserError("Input must be a non-empty string")
        
        try:
            raw_blocks = self._get_raw_blocks(input_str)
            shape_blocks = []
            
            for block in raw_blocks:
                try:
                    shape_block = self._parse_block(block)
                    if shape_block:
                        shape_blocks.append(shape_block)
                except Exception as e:
                    logger.warning(f"Failed to parse block: {e}")
                    continue
            
            return shape_blocks
            
        except Exception as e:
            raise ParserError(f"Failed to parse input: {e}") from e
    
    def _parse_block(self, block: str) -> Optional[ShapeBlock]:
        """Parse a single block of TikZ code into a ShapeBlock."""
        lines = block.strip().split('\n')
        if not lines:
            return None
            
        annotation_line = lines[0].strip() if lines else ""
        raw_block = '\n'.join(lines[1:]).strip() if len(lines) > 1 else ""
        
        shape_type, shape_id = self._extract_shape_info(annotation_line)
        raw_shape_data, raw_arrows_data = self._extract_shape_and_arrows(raw_block)
        
        return ShapeBlock(
            raw_block=raw_block,
            annotation=annotation_line,
            shape_type=shape_type,
            shape_id=shape_id,
            raw_shape_data=raw_shape_data,
            raw_arrows_data=raw_arrows_data
        )
    
    def _get_raw_blocks(self, input_str: str) -> List[str]:
        """
        Split input string into raw blocks.
        
        Args:
            input_str: Input string to split
            
        Returns:
            List of raw block strings
        """
        # Debug: log first 100 chars of input to aid troubleshooting
        logger.debug(f"Input preview: {input_str[:100]}...")
        blocks = []
        lines = input_str.split('\n')
        current_block = []
        in_block = False
        
        logger.debug(f"Supported shape types: {self.supported_shape_types}")
        
        for i, line in enumerate(lines):
            line_stripped = line.strip()
            logger.debug(f"Line {i+1}: {line_stripped}")
            
            # Start of a new block - check for any supported shape type (case-insensitive)
            if line_stripped.startswith('%'):
                logger.debug(f"Found comment line: {line_stripped}")
                line_lower = line_stripped.lower()
                matched_supported = False
                for shape_type in self.supported_shape_types:
                    if shape_type.lower() in line_lower:
                        logger.debug(f"Found shape type '{shape_type}' in line")
                        # If we were already in a block, save it
                        if in_block and current_block:
                            blocks.append('\n'.join(current_block))
                        # Start a new block
                        current_block = [line]
                        in_block = True
                        logger.debug(f"Started new block for shape type: {shape_type}")
                        matched_supported = True
                        break  # No need to check other shape types

                if not matched_supported:
                    # Fallbacks to start a new block for unknown annotations
                    start_new = False
                    if re.search(r'%.*\[id:', line_stripped, re.IGNORECASE):
                        logger.debug("Treating comment with [id:] as start of unknown shape block")
                        start_new = True
                    elif re.search(r'%\s*Shape\s*:', line_stripped, re.IGNORECASE):
                        logger.debug("Treating '%Shape:' annotation as start of block")
                        start_new = True
                    elif re.search(r'%\s*(Text\s+Node|Text|Node)\b', line_stripped, re.IGNORECASE):
                        logger.debug("Treating '%Text Node', '%Text', or '%Node' as start of block")
                        start_new = True

                    if start_new:
                        if in_block and current_block:
                            blocks.append('\n'.join(current_block))
                        current_block = [line]
                        in_block = True
                    elif in_block:
                        logger.debug("Continuing current block with comment line")
                        current_block.append(line)
            # Continue current block
            elif in_block:
                # End of block if we've reached the end of tikzpicture or a new shape annotation
                if '\\end{tikzpicture}' in line:
                    # Don't include the end tag in the block
                    in_block = False
                    blocks.append('\n'.join(current_block))
                    current_block = []
                else:
                    ls = line.lstrip()
                    # Keep typical TikZ statements inside the block: any command starting with '\\' (e.g., \\draw, \\node, \\path, ...),
                    # comments, or empty lines.
                    if not ls:
                        current_block.append(line)
                    elif ls.startswith('%'):
                        current_block.append(line)
                    elif ls.startswith('\\'):
                        current_block.append(line)
                    else:
                        # Non-TikZ content ends the current block
                        in_block = False
                        blocks.append('\n'.join(current_block))
                        current_block = []
        
        # Add the last block if there is one
        if in_block and current_block:
            blocks.append('\n'.join(current_block))
        
        return blocks
    
    def _extract_shape_info(self, annotation: str) -> tuple:
        """
        Extract shape type and ID from annotation line.
        
        Args:
            annotation: The annotation line from the shape block
            
        Returns:
            Tuple of (shape_type, shape_id)
        """
        shape_type = None
        shape_id = None
        
        # Extract shape type
        for supported_type in self.supported_shape_types:
            if supported_type in annotation:
                shape_type = supported_type
                break

        if not shape_type:
            # Fallback: capture any text after optional "Shape:" prefix
            match = re.search(r'%\s*(?:Shape:)?\s*([^\[\n]+)', annotation)
            if match:
                shape_type = match.group(1).strip()
        
        # Extract shape ID using regex
        id_match = re.search(r'\[id:([^\]]+)\]', annotation)
        if id_match:
            shape_id = id_match.group(1)
        
        return shape_type, shape_id
    
    def _extract_shape_and_arrows(self, raw_block: str) -> tuple:
        """
        Extract shape and arrow data from raw block.
        
        Args:
            raw_block: Raw block to parse
            
        Returns:
            Tuple of (shape_data, arrows_data)
        """
        # Split the raw block into lines
        lines = raw_block.split('\n')
        shape_lines = []
        arrow_lines = []
        
        for line in lines:
            if line.strip():
                if self._is_arrow_line(line):
                    arrow_lines.append(line)
                else:
                    shape_lines.append(line)

        raw_shape_data = '\n'.join(shape_lines)
        raw_arrows_data = '\n'.join(arrow_lines)

        return raw_shape_data, raw_arrows_data

    def _is_arrow_line(self, line: str) -> bool:
        """Determine whether a single TikZ command line represents part of an arrow."""

        stripped = line.strip()
        if not stripped:
            return False

        # Arrow heads exported by Mathcha use a shift/rotate style combination.
        shift_rotate_pattern = re.search(
            r'\[([^\]]*?)shift=\{\s*\([^}]+\)\s*\}[^\]]*rotate\s*=\s*[-+0-9.]+' ,
            stripped,
            re.IGNORECASE,
        )
        if shift_rotate_pattern:
            return True

        return False
