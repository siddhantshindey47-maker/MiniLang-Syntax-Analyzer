"""
lexer.py - Lexical Analyzer (Lexer/Scanner) for MiniLang
=========================================================

WHAT IS A LEXER?
  A Lexical Analyzer (Lexer) is the first phase of a compiler.
  It reads raw source code character by character and groups them
  into meaningful units called TOKENS.

  Think of it like reading a sentence:
    "The cat sat" -> ["The", "cat", "sat"]  (words)
  
  Similarly:
    "int x = 10;" -> [KEYWORD:int, ID:x, ASSIGN:=, NUMBER:10, SEMICOLON:;]

HOW THIS LEXER WORKS:
  1. Start at position 0 of the source code
  2. Skip whitespace and comments
  3. Look at the current character(s)
  4. Determine what kind of token it is:
     - If it starts with a letter/underscore -> keyword or identifier
     - If it starts with a digit -> number
     - If it starts with '"' -> string
     - If it's an operator or separator -> corresponding token
  5. Create a Token object and add it to the token list
  6. Move to the next position
  7. Repeat until end of input
  8. Add an EOF token

The lexer also tracks line and column numbers for error reporting.
"""

from .tokens import Token, TokenType, KEYWORDS


class LexerError:
    """Represents an error encountered during lexical analysis."""
    
    def __init__(self, message: str, line: int, column: int):
        self.message = message
        self.line = line
        self.column = column
    
    def to_dict(self) -> dict:
        return {
            "message": self.message,
            "line": self.line,
            "column": self.column
        }


class Lexer:
    """
    The MiniLang Lexical Analyzer.
    
    Converts source code (string) into a list of tokens.
    
    Usage:
        lexer = Lexer("int x = 10;")
        tokens, errors = lexer.tokenize()
    """
    
    def __init__(self, source: str):
        self.source = source        # The source code to tokenize
        self.pos = 0                # Current position in the source
        self.line = 1               # Current line number (1-indexed)
        self.column = 1             # Current column number (1-indexed)
        self.tokens = []            # List of tokens produced
        self.errors = []            # List of lexer errors
    
    # ─── Helper Methods ───────────────────────────────────────────
    
    def current_char(self) -> str:
        """Return the character at the current position, or None if at end."""
        if self.pos < len(self.source):
            return self.source[self.pos]
        return None
    
    def peek(self) -> str:
        """Look at the next character without consuming it."""
        if self.pos + 1 < len(self.source):
            return self.source[self.pos + 1]
        return None
    
    def advance(self) -> str:
        """
        Consume the current character and move to the next.
        Updates line/column tracking for newlines.
        """
        char = self.current_char()
        self.pos += 1
        if char == '\n':
            self.line += 1
            self.column = 1
        else:
            self.column += 1
        return char
    
    def add_token(self, token_type: str, value: str, line: int, column: int):
        """Create a token and add it to the token list."""
        self.tokens.append(Token(token_type, value, line, column))
    
    def add_error(self, message: str, line: int, column: int):
        """Record a lexer error."""
        self.errors.append(LexerError(message, line, column))
    
    # ─── Whitespace and Comment Handling ──────────────────────────
    
    def skip_whitespace(self):
        """Skip spaces, tabs, newlines, and carriage returns."""
        while self.current_char() is not None and self.current_char() in ' \t\n\r':
            self.advance()
    
    def skip_comment(self):
        """
        Skip single-line comments: // ... until end of line
        Comments are ignored during tokenization.
        """
        # We already know current char is '/' and next is '/'
        self.advance()  # skip first /
        self.advance()  # skip second /
        # Skip until end of line or end of input
        while self.current_char() is not None and self.current_char() != '\n':
            self.advance()
    
    # ─── Token Recognition Methods ───────────────────────────────
    
    def read_identifier_or_keyword(self):
        """
        Read an identifier or keyword.
        
        Identifiers: [A-Za-z_][A-Za-z0-9_]*
        Keywords: int, float, bool, if, else, while, print, true, false
        
        After reading, we check if the word is a keyword.
        If it's 'true' or 'false', it's a BOOLEAN literal.
        """
        start_line = self.line
        start_col = self.column
        result = ""
        
        # Read all alphanumeric characters and underscores
        while self.current_char() is not None and (self.current_char().isalnum() or self.current_char() == '_'):
            result += self.advance()
        
        # Check if it's a keyword, boolean, or identifier
        if result in ("true", "false"):
            self.add_token(TokenType.BOOLEAN, result, start_line, start_col)
        elif result in KEYWORDS:
            self.add_token(TokenType.KEYWORD, result, start_line, start_col)
        else:
            self.add_token(TokenType.ID, result, start_line, start_col)
    
    def read_number(self):
        """
        Read a number literal (integer or float).
        
        Integer: [0-9]+
        Float:   [0-9]+ "." [0-9]+
        """
        start_line = self.line
        start_col = self.column
        result = ""
        
        # Read integer part
        while self.current_char() is not None and self.current_char().isdigit():
            result += self.advance()
        
        # Check for decimal point (float)
        if self.current_char() == '.' and self.peek() is not None and self.peek().isdigit():
            result += self.advance()  # consume '.'
            while self.current_char() is not None and self.current_char().isdigit():
                result += self.advance()
        
        self.add_token(TokenType.NUMBER, result, start_line, start_col)
    
    def read_string(self):
        """
        Read a string literal: "..."
        
        The opening quote has already been identified.
        We read until the closing quote or end of input.
        """
        start_line = self.line
        start_col = self.column
        self.advance()  # skip opening quote
        result = ""
        
        while self.current_char() is not None and self.current_char() != '"':
            if self.current_char() == '\n':
                # Strings cannot span multiple lines in MiniLang
                self.add_error("Unterminated string literal", start_line, start_col)
                return
            result += self.advance()
        
        if self.current_char() == '"':
            self.advance()  # skip closing quote
            self.add_token(TokenType.STRING, result, start_line, start_col)
        else:
            self.add_error("Unterminated string literal", start_line, start_col)
    
    # ─── Main Tokenization Loop ──────────────────────────────────
    
    def tokenize(self) -> tuple:
        """
        Main tokenization method.
        
        Scans the entire source code and produces a list of tokens.
        
        Returns:
            tuple: (list of Token objects, list of LexerError objects)
        """
        while self.current_char() is not None:
            # Skip whitespace
            self.skip_whitespace()
            
            if self.current_char() is None:
                break
            
            char = self.current_char()
            
            # ── Comments ──
            if char == '/' and self.peek() == '/':
                self.skip_comment()
                continue
            
            # ── Identifiers and Keywords ──
            if char.isalpha() or char == '_':
                self.read_identifier_or_keyword()
                continue
            
            # ── Numbers ──
            if char.isdigit():
                self.read_number()
                continue
            
            # ── Strings ──
            if char == '"':
                self.read_string()
                continue
            
            # ── Two-character operators ──
            # We check two-character operators first to avoid ambiguity
            # e.g., "==" should not be tokenized as "=" + "="
            
            start_line = self.line
            start_col = self.column
            
            if char == '=' and self.peek() == '=':
                self.advance()
                self.advance()
                self.add_token(TokenType.EQUAL, "==", start_line, start_col)
                continue
            
            if char == '!' and self.peek() == '=':
                self.advance()
                self.advance()
                self.add_token(TokenType.NOT_EQUAL, "!=", start_line, start_col)
                continue
            
            if char == '<' and self.peek() == '=':
                self.advance()
                self.advance()
                self.add_token(TokenType.LESS_EQ, "<=", start_line, start_col)
                continue
            
            if char == '>' and self.peek() == '=':
                self.advance()
                self.advance()
                self.add_token(TokenType.GREATER_EQ, ">=", start_line, start_col)
                continue
            
            if char == '&' and self.peek() == '&':
                self.advance()
                self.advance()
                self.add_token(TokenType.AND, "&&", start_line, start_col)
                continue
            
            if char == '|' and self.peek() == '|':
                self.advance()
                self.advance()
                self.add_token(TokenType.OR, "||", start_line, start_col)
                continue
            
            # ── Single-character operators ──
            if char == '+':
                self.advance()
                self.add_token(TokenType.PLUS, "+", start_line, start_col)
                continue
            
            if char == '-':
                self.advance()
                self.add_token(TokenType.MINUS, "-", start_line, start_col)
                continue
            
            if char == '*':
                self.advance()
                self.add_token(TokenType.MULTIPLY, "*", start_line, start_col)
                continue
            
            if char == '/':
                self.advance()
                self.add_token(TokenType.DIVIDE, "/", start_line, start_col)
                continue
            
            if char == '%':
                self.advance()
                self.add_token(TokenType.MODULO, "%", start_line, start_col)
                continue
            
            if char == '=':
                self.advance()
                self.add_token(TokenType.ASSIGN, "=", start_line, start_col)
                continue
            
            if char == '!':
                self.advance()
                self.add_token(TokenType.NOT, "!", start_line, start_col)
                continue
            
            if char == '<':
                self.advance()
                self.add_token(TokenType.LESS, "<", start_line, start_col)
                continue
            
            if char == '>':
                self.advance()
                self.add_token(TokenType.GREATER, ">", start_line, start_col)
                continue
            
            # ── Separators ──
            if char == '(':
                self.advance()
                self.add_token(TokenType.LPAREN, "(", start_line, start_col)
                continue
            
            if char == ')':
                self.advance()
                self.add_token(TokenType.RPAREN, ")", start_line, start_col)
                continue
            
            if char == '{':
                self.advance()
                self.add_token(TokenType.LBRACE, "{", start_line, start_col)
                continue
            
            if char == '}':
                self.advance()
                self.add_token(TokenType.RBRACE, "}", start_line, start_col)
                continue
            
            if char == ';':
                self.advance()
                self.add_token(TokenType.SEMICOLON, ";", start_line, start_col)
                continue
            
            # ── Unrecognized character ──
            self.add_error(
                f"Unexpected character '{char}'",
                start_line,
                start_col
            )
            self.advance()  # Skip the bad character and continue
        
        # Add EOF token to signal end of input to the parser
        self.add_token(TokenType.EOF, "EOF", self.line, self.column)
        
        return self.tokens, self.errors
