"""
tokens.py - Token Definitions for MiniLang
==========================================

In compiler construction, a TOKEN is the smallest meaningful unit of a program.
The lexer reads raw source code (a stream of characters) and groups them into tokens.

Each token has:
  - type  : What kind of token it is (keyword, identifier, number, etc.)
  - value : The actual text of the token
  - line  : Line number where the token appears (for error reporting)
  - column: Column number where the token starts (for error reporting)

Example:
  Source: "int x = 10;"
  Tokens: [KEYWORD:int, ID:x, ASSIGN:=, NUMBER:10, SEMICOLON:;]
"""


class TokenType:
    """
    Enumeration of all token types recognized by MiniLang.
    
    We use string constants instead of Python's enum for simplicity
    and readability — easier to understand in a viva.
    """
    
    # --- Keywords ---
    # These are reserved words in MiniLang that have special meaning.
    KEYWORD = "KEYWORD"
    
    # --- Identifiers ---
    # Variable names like x, price, myVar, etc.
    ID = "ID"
    
    # --- Literals ---
    # Constant values that appear directly in the code.
    NUMBER = "NUMBER"        # Integer or float literals: 10, 3.14
    STRING = "STRING"        # String literals: "Hello"
    BOOLEAN = "BOOLEAN"      # true, false
    
    # --- Arithmetic Operators ---
    PLUS = "PLUS"            # +
    MINUS = "MINUS"          # -
    MULTIPLY = "MULTIPLY"    # *
    DIVIDE = "DIVIDE"        # /
    MODULO = "MODULO"        # %
    
    # --- Assignment ---
    ASSIGN = "ASSIGN"        # =
    
    # --- Comparison / Relational Operators ---
    EQUAL = "EQUAL"          # ==
    NOT_EQUAL = "NOT_EQUAL"  # !=
    LESS = "LESS"            # <
    GREATER = "GREATER"      # >
    LESS_EQ = "LESS_EQ"      # <=
    GREATER_EQ = "GREATER_EQ"  # >=
    
    # --- Logical Operators ---
    AND = "AND"              # &&
    OR = "OR"                # ||
    NOT = "NOT"              # !
    
    # --- Separators / Delimiters ---
    LPAREN = "LPAREN"        # (
    RPAREN = "RPAREN"        # )
    LBRACE = "LBRACE"        # {
    RBRACE = "RBRACE"        # }
    SEMICOLON = "SEMICOLON"  # ;
    
    # --- Special ---
    EOF = "EOF"              # End of file / end of input


# Set of all MiniLang keywords
KEYWORDS = {"int", "float", "bool", "if", "else", "while", "print", "true", "false"}


class Token:
    """
    Represents a single token produced by the lexer.
    
    Attributes:
        type   (str): The token type (from TokenType constants)
        value  (str): The actual text value of the token
        line   (int): Line number (1-indexed) where the token starts
        column (int): Column number (1-indexed) where the token starts
    """
    
    def __init__(self, type: str, value: str, line: int, column: int):
        self.type = type
        self.value = value
        self.line = line
        self.column = column
    
    def __repr__(self) -> str:
        return f"Token({self.type}, '{self.value}', line={self.line}, col={self.column})"
    
    def to_dict(self) -> dict:
        """Convert token to dictionary for JSON serialization (used by Flask API)."""
        return {
            "type": self.type,
            "value": self.value,
            "line": self.line,
            "column": self.column
        }
