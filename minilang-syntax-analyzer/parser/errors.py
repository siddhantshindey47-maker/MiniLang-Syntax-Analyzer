"""
errors.py - Syntax Error Handling for MiniLang
================================================

Good error messages are crucial in a compiler. When a programmer writes
incorrect code, the compiler should:
  1. Tell them WHAT went wrong
  2. Tell them WHERE it went wrong (line and column)
  3. Tell them WHAT was expected

This module defines the SyntaxError class used by the parser.

Error Recovery:
  Our parser implements "panic mode" error recovery:
  - When an error is found, record the error message
  - Try to skip tokens until we find a synchronization point
    (like a semicolon or closing brace)
  - Continue parsing to find more errors
  
  This allows reporting multiple errors in one pass instead of
  stopping at the first error.
"""


class SyntaxError:
    """
    Represents a syntax error found during parsing.
    
    Attributes:
        message (str): Human-readable description of the error
        line    (int): Line number where the error was detected
        column  (int): Column number where the error was detected
    """
    
    def __init__(self, message: str, line: int, column: int):
        self.message = message
        self.line = line
        self.column = column
    
    def __repr__(self) -> str:
        return f"SyntaxError(line={self.line}, col={self.column}: {self.message})"
    
    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization (used by Flask API)."""
        return {
            "message": self.message,
            "line": self.line,
            "column": self.column
        }
