"""
TikZ Lexer

Provides tokenization of TikZ code into a sequence of tokens for further processing.
Uses the existing regex_cache and regex_patterns utilities for pattern matching.
"""

from typing import List, Tuple, Optional, Dict, Pattern
import re
from dataclasses import dataclass
from enum import Enum, auto

from utils.cache.regex_cache import regex_cache, CommonPatterns
from utils.cache.regex_patterns import regex_patterns


class TokenType(Enum):
    """Types of tokens in TikZ code."""
    COMMENT = auto()
    COMMAND = auto()
    COORD = auto()
    NUMBER = auto()
    STRING = auto()
    SYMBOL = auto()
    WHITESPACE = auto()
    IDENTIFIER = auto()
    SHAPE_TYPE = auto()
    SHAPE_ID = auto()
    RAW_BLOCK = auto()
    UNKNOWN = auto()


@dataclass
class Token:
    """Represents a single token in the TikZ code."""
    token_type: TokenType
    value: str
    line: int = 0
    column: int = 0


class TikzLexer:
    """
    Lexer for TikZ code that tokenizes input strings into a sequence of tokens.
    Uses the existing regex_cache and regex_patterns for pattern matching.
    """
    
    # Pre-compiled patterns using regex_cache
    PATTERNS: List[Tuple[TokenType, Pattern]] = [
        # Shape types with IDs (e.g., %Shape: Straight Lines [id:...])
        (TokenType.SHAPE_TYPE, regex_cache.compile(r'%Shape:\s*([^\n\[]+?)(?:\s*\[id:([^\]]+)\])?\s*$')),
        # Comments (start with % but not %Shape:)
        (TokenType.COMMENT, regex_cache.compile(r'%(?!Shape:)[^\n]*')),
        # Standalone shape IDs (e.g., [id:dp123])
        (TokenType.SHAPE_ID, regex_cache.compile(r'\[id:([^\]]+)\]')),
        # Commands (start with \)
        (TokenType.COMMAND, regex_cache.compile(r'\\([a-zA-Z]+)')),
        # Coordinates (in parentheses)
        (TokenType.COORD, regex_cache.compile(r'(\([^()]*(?:\([^()]*\)[^()]*)*\))')),
        # Numbers (integers and floats)
        (TokenType.NUMBER, regex_cache.compile(r'[-+]?\d*\.\d+|[-+]?\d+')),
        # Strings (in curly braces)
        (TokenType.STRING, regex_cache.compile(r'\{([^}]*)\}(?!\s*\{)')),  # Non-greedy match for single {}
        # Arrow symbols (--, ->, <-, <->, etc.)
        (TokenType.SYMBOL, regex_cache.compile(r'--|->|<-|<-?>|\+>|\+<|\+->|\+-<')),
        # Other symbols
        (TokenType.SYMBOL, regex_cache.compile(r'[=,\[\]();]')),
        # Identifiers (variable names, etc.)
        (TokenType.IDENTIFIER, regex_cache.compile(r'[a-zA-Z_][a-zA-Z0-9_:]*')),
        # Whitespace (skip)
        (TokenType.WHITESPACE, regex_cache.compile(r'\s+')),
    ]
    
    def __init__(self):
        """Initialize the lexer."""
        self.tokens: List[Token] = []
        self.current_line = 1
        self.current_column = 1
    
    def tokenize(self, input_str: str) -> List[Token]:
        """
        Tokenize the input string into a list of tokens.
        
        Args:
            input_str: The input TikZ code to tokenize
            
        Returns:
            List of Token objects
        """
        self.tokens = []
        self.current_line = 1
        self.current_column = 1
        
        # Split into lines to handle line numbers correctly
        lines = input_str.splitlines()
        
        for line_num, line in enumerate(lines, 1):
            self.current_line = line_num
            self.current_column = 1
            pos = 0
            line_len = len(line)
            
            # Skip empty lines
            if not line.strip():
                continue
                
            # Debug output for the current line being processed
            print(f"\nProcessing line {line_num}: {line!r}")
            
            # First, check if this is a shape definition line
            # It can start with %Shape: or %Straight Lines
            shape_match = re.match(r'%(Shape|Straight Lines)\s*([^\n\[]*?)(?:\s*\[id:([^\]]+)\])?\s*$', line.strip())
            if shape_match:
                shape_type = shape_match.group(1)
                shape_name = shape_match.group(2).strip()
                shape_id = shape_match.group(3) if shape_match.lastindex and shape_match.lastindex > 2 and shape_match.group(3) else None
                
                # If we matched 'Straight Lines', use that as the shape name
                if shape_type == 'Straight Lines':
                    shape_name = 'Straight Lines'
                
                # Add the shape type token
                self.tokens.append(Token(
                    token_type=TokenType.SHAPE_TYPE,
                    value=shape_name,
                    line=self.current_line,
                    column=self.current_column + line.find(shape_type)
                ))
                
                # If there's an ID, add it as a separate token
                if shape_id:
                    self.tokens.append(Token(
                        token_type=TokenType.SHAPE_ID,
                        value=shape_id,
                        line=self.current_line,
                        column=self.current_column + line.find('[id:')
                    ))
                
                # Move to the next line
                continue
            
            # Process the rest of the line normally
            while pos < line_len:
                # Skip whitespace
                if line[pos].isspace():
                    self.current_column += 1
                    pos += 1
                    continue
                
                # Try to match patterns
                match = None
                for token_type, pattern in self.PATTERNS:
                    match = pattern.match(line, pos)
                    if match:
                        value = match.group(0)
                        start_pos = match.start()
                        end_pos = match.end()
                        
                        # Debug output for the match
                        print(f"  Match at pos {pos}-{end_pos}: {token_type.name} = {value!r}")
                        
                        # Update column position
                        self.current_column += (start_pos - pos)
                        
                        # Handle shape types and their optional IDs
                        if token_type == TokenType.SHAPE_TYPE:
                            print(f"    Groups: {match.groups()}")
                            shape_name = match.group(1).strip()
                            shape_id = match.group(2) if match.lastindex and match.lastindex > 1 and match.group(2) else None
                            
                            # Add the shape type token
                            self.tokens.append(Token(
                                token_type=TokenType.SHAPE_TYPE,
                                value=shape_name,
                                line=self.current_line,
                                column=self.current_column
                            ))
                            
                            # If there's an ID in the same line, add it as a separate token
                            if shape_id:
                                self.tokens.append(Token(
                                    token_type=TokenType.SHAPE_ID,
                                    value=shape_id,
                                    line=self.current_line,
                                    column=self.current_column + match.start(2) - 4  # Adjust for [id: prefix and %Shape:
                                ))
                            
                            # Update position and continue to next token
                            token_length = end_pos - start_pos
                            self.current_column += token_length
                            pos = end_pos
                            continue
                        
                        # Skip whitespace tokens
                        if token_type != TokenType.WHITESPACE:
                            # For standalone shape IDs
                            if token_type == TokenType.SHAPE_ID and len(match.groups()) > 0:
                                value = match.group(1).strip()
                                self.tokens.append(Token(
                                    token_type=token_type,
                                    value=value,
                                    line=self.current_line,
                                    column=self.current_column
                                ))
                            # For other token types
                            else:
                                self.tokens.append(Token(
                                    token_type=token_type,
                                    value=value,
                                    line=self.current_line,
                                    column=self.current_column
                                ))
                            # Update position
                            token_length = end_pos - start_pos
                            self.current_column += token_length
                            pos = end_pos
                            continue
                
                # If no pattern matched, move to next character
                if not match:
                    # Check if we've reached the end of the line
                    if pos >= line_len:
                        break
                        
                    # Check if this is a potential command (starts with \)
                    if line[pos] == '\\':
                        # Try to match a command
                        cmd_match = re.match(r'\\([a-zA-Z]+)', line[pos:])
                        if cmd_match:
                            value = cmd_match.group(0)
                            self.tokens.append(Token(
                                token_type=TokenType.COMMAND,
                                value=value[1:],  # Remove the backslash
                                line=self.current_line,
                                column=self.current_column
                            ))
                            token_length = len(value)
                            self.current_column += token_length
                            pos += token_length
                            continue
                    
                    # If we get here, we couldn't match anything, so just skip the character
                    print(f"Warning: Unrecognized character '{line[pos]}' at line {self.current_line}, column {self.current_column}")
                    pos += 1
                    self.current_column += 1
        
        return self.tokens
    
    def get_tokens_by_type(self, token_type: TokenType) -> List[Token]:
        """
        Get all tokens of a specific type.
        
        Args:
            token_type: The type of tokens to retrieve
            
        Returns:
            List of matching tokens
        """
        return [token for token in self.tokens if token.token_type == token_type]
    
    def get_token_values(self) -> List[str]:
        """
        Get a list of token values.
        
        Returns:
            List of token values as strings
        """
        return [token.value for token in self.tokens]
    
    def __str__(self) -> str:
        """Return a string representation of the tokens."""
        return '\n'.join(f"{token.token_type.name}: {token.value!r} "
                         f"(line {token.line}, col {token.column})" 
                         for token in self.tokens)
