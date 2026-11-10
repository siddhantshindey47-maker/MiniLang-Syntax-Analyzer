"""
parser.py - Recursive Descent Parser for MiniLang
===================================================

WHAT IS A PARSER?
  The parser is the second phase of a compiler. It takes the stream of tokens
  produced by the lexer and checks whether they follow the grammar rules
  of the language (syntax analysis).

  Think of grammar as the "sentence structure" of a language:
    English: Subject + Verb + Object  (e.g., "The cat sat")
    MiniLang: type + ID + "=" + expression + ";"  (e.g., "int x = 10;")

WHAT IS RECURSIVE DESCENT?
  Recursive Descent is a top-down parsing technique where:
  - Each grammar rule becomes a Python function
  - The parser starts from the top rule (program) and works down
  - It "descends" into sub-rules by calling their functions
  - It's called "recursive" because rules can call each other recursively

  Example:
    parse_program() calls parse_statement_list()
    parse_statement_list() calls parse_statement()
    parse_statement() calls parse_declaration() or parse_assignment() etc.
    parse_declaration() calls parse_expression()
    parse_expression() calls parse_additive()
    parse_additive() calls parse_term()
    ... and so on

WHY RECURSIVE DESCENT?
  - Easy to understand and implement manually
  - Each function directly corresponds to a grammar rule
  - Easy to explain in a viva!
  - No parser-generator tools needed

OPERATOR PRECEDENCE:
  The expression grammar is designed so that operators with lower
  precedence are parsed at higher levels of the call tree:
  
  parse_expression() -> Lowest precedence (||)
    └── parse_logical_or()
        └── parse_logical_and()    (&&)
            └── parse_equality()   (==, !=)
                └── parse_relational()  (<, >, <=, >=)
                    └── parse_additive()  (+, -)
                        └── parse_term()  (*, /, %)
                            └── parse_factor()  (numbers, ids, parens)
  
  This ensures that * binds tighter than +, which binds tighter than ==, etc.
"""

from lexer.tokens import Token, TokenType
from parser.ast_nodes import (
    Program, Declaration, Assignment, IfStatement, WhileStatement,
    PrintStatement, Block, BinaryExpression, UnaryExpression,
    Literal, Identifier
)
from parser.errors import SyntaxError


class Parser:
    """
    Recursive Descent Parser for MiniLang.
    
    Consumes a list of tokens and produces an AST (Abstract Syntax Tree).
    
    Usage:
        parser = Parser(tokens)
        ast, errors = parser.parse()
    """
    
    def __init__(self, tokens: list):
        self.tokens = tokens       # List of Token objects from the lexer
        self.pos = 0               # Current position in the token list
        self.errors = []           # List of syntax errors found
    
    # ─────────────────────────────────────────────────────────────
    #  HELPER METHODS
    #  These are utility functions used by all parsing functions.
    # ─────────────────────────────────────────────────────────────
    
    def current_token(self) -> Token:
        """
        Return the current token (the one we're about to process).
        If we've gone past the end, return the last token (EOF).
        """
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return self.tokens[-1]  # EOF token
    
    def peek_token(self) -> Token:
        """Look at the next token without consuming the current one."""
        if self.pos + 1 < len(self.tokens):
            return self.tokens[self.pos + 1]
        return self.tokens[-1]
    
    def advance(self) -> Token:
        """Consume the current token and move to the next one."""
        token = self.current_token()
        if self.pos < len(self.tokens) - 1:  # Don't advance past EOF
            self.pos += 1
        return token
    
    def match(self, token_type: str, value: str = None) -> bool:
        """
        Check if the current token matches the expected type (and optionally value).
        Does NOT consume the token.
        """
        token = self.current_token()
        if token.type != token_type:
            return False
        if value is not None and token.value != value:
            return False
        return True
    
    def expect(self, token_type: str, value: str = None, error_msg: str = None) -> Token:
        """
        Assert that the current token matches, then consume it.
        If it doesn't match, record a syntax error.
        
        This is the key function for error detection.
        """
        if self.match(token_type, value):
            return self.advance()
        
        # ── Error: unexpected token ──
        token = self.current_token()
        if error_msg:
            msg = error_msg
        elif value:
            msg = f"Expected '{value}' but found '{token.value}'"
        else:
            msg = f"Expected {token_type} but found '{token.value}' ({token.type})"
        
        self.errors.append(SyntaxError(msg, token.line, token.column))
        return None
    
    def add_error(self, message: str, line: int = None, column: int = None):
        """Add a syntax error at the current position."""
        token = self.current_token()
        self.errors.append(SyntaxError(
            message,
            line or token.line,
            column or token.column
        ))
    
    def synchronize(self):
        """
        Panic-mode error recovery.
        
        When a syntax error is found, skip tokens until we reach a
        "synchronization point" — a place where we can safely resume parsing.
        
        Synchronization points:
          - Semicolons (end of statement)
          - Closing braces (end of block)
          - Keywords that start statements (int, float, bool, if, while, print)
        """
        while not self.match(TokenType.EOF):
            # Stop at semicolons — end of a statement
            if self.match(TokenType.SEMICOLON):
                self.advance()
                return
            # Stop at closing braces — end of a block
            if self.match(TokenType.RBRACE):
                return
            # Stop at statement-starting keywords
            if self.match(TokenType.KEYWORD) and self.current_token().value in (
                "int", "float", "bool", "if", "while", "print"
            ):
                return
            self.advance()
    
    # ─────────────────────────────────────────────────────────────
    #  MAIN PARSE METHOD
    # ─────────────────────────────────────────────────────────────
    
    def parse(self) -> tuple:
        """
        Entry point for parsing.
        
        Returns:
            tuple: (AST root node or None, list of SyntaxError objects)
        """
        program = self.parse_program()
        return program, self.errors
    
    # ─────────────────────────────────────────────────────────────
    #  GRAMMAR RULE: program -> statement_list
    # ─────────────────────────────────────────────────────────────
    
    def parse_program(self) -> Program:
        """Parse the entire program (top-level rule)."""
        statements = self.parse_statement_list()
        return Program(statements)
    
    # ─────────────────────────────────────────────────────────────
    #  GRAMMAR RULE: statement_list -> statement statement_list | ε
    # ─────────────────────────────────────────────────────────────
    
    def parse_statement_list(self) -> list:
        """
        Parse a list of statements until we hit EOF or a closing brace.
        The ε (epsilon) production means this list can be empty.
        """
        statements = []
        
        while not self.match(TokenType.EOF) and not self.match(TokenType.RBRACE):
            stmt = self.parse_statement()
            if stmt is not None:
                statements.append(stmt)
        
        return statements
    
    # ─────────────────────────────────────────────────────────────
    #  GRAMMAR RULE: statement -> declaration | assignment | 
    #                             if_statement | while_statement |
    #                             print_statement | block
    # ─────────────────────────────────────────────────────────────
    
    def parse_statement(self):
        """
        Determine which type of statement we're looking at and parse it.
        
        We use LOOKAHEAD to decide:
          - If current token is a type keyword (int/float/bool) -> declaration
          - If current token is an identifier AND next is '=' -> assignment
          - If current token is 'if' -> if_statement
          - If current token is 'while' -> while_statement
          - If current token is 'print' -> print_statement
          - If current token is '{' -> block
          - Otherwise -> syntax error
        """
        token = self.current_token()
        
        # Declaration: starts with a type keyword
        if token.type == TokenType.KEYWORD and token.value in ("int", "float", "bool"):
            return self.parse_declaration()
        
        # Assignment: starts with an identifier followed by '='
        if token.type == TokenType.ID and self.peek_token().type == TokenType.ASSIGN:
            return self.parse_assignment()
        
        # If statement
        if token.type == TokenType.KEYWORD and token.value == "if":
            return self.parse_if_statement()
        
        # While statement
        if token.type == TokenType.KEYWORD and token.value == "while":
            return self.parse_while_statement()
        
        # Print statement
        if token.type == TokenType.KEYWORD and token.value == "print":
            return self.parse_print_statement()
        
        # Block
        if token.type == TokenType.LBRACE:
            return self.parse_block()
        
        # ── Error: unrecognized statement ──
        self.add_error(
            f"Unexpected token '{token.value}'. Expected a statement "
            f"(declaration, assignment, if, while, print, or block)."
        )
        self.synchronize()
        return None
    
    # ─────────────────────────────────────────────────────────────
    #  GRAMMAR RULE: declaration -> type ID declaration_init ";"
    #  declaration_init -> "=" expression | ε
    # ─────────────────────────────────────────────────────────────
    
    def parse_declaration(self) -> Declaration:
        """
        Parse a variable declaration.
        Examples: int x;    float price = 25.5;
        """
        # Parse type keyword
        type_token = self.advance()  # consume int/float/bool
        var_type = type_token.value
        line = type_token.line
        
        # Parse variable name (identifier)
        name_token = self.expect(
            TokenType.ID,
            error_msg=f"Expected variable name after '{var_type}'"
        )
        if name_token is None:
            self.synchronize()
            return None
        name = name_token.value
        
        # Check for optional initialization: = expression
        init_value = None
        if self.match(TokenType.ASSIGN):
            self.advance()  # consume '='
            init_value = self.parse_expression()
            if init_value is None:
                self.add_error(f"Expected expression after '=' in declaration of '{name}'")
                self.synchronize()
                return Declaration(var_type, name, None, line)
        
        # Expect semicolon at end
        self.expect(
            TokenType.SEMICOLON,
            error_msg=f"Expected ';' after variable declaration"
        )
        
        return Declaration(var_type, name, init_value, line)
    
    # ─────────────────────────────────────────────────────────────
    #  GRAMMAR RULE: assignment -> ID "=" expression ";"
    # ─────────────────────────────────────────────────────────────
    
    def parse_assignment(self) -> Assignment:
        """
        Parse an assignment statement.
        Example: x = 10 + 5;
        """
        name_token = self.advance()  # consume identifier
        name = name_token.value
        line = name_token.line
        
        self.expect(TokenType.ASSIGN, error_msg="Expected '=' in assignment")
        
        value = self.parse_expression()
        if value is None:
            self.add_error(f"Expected expression after '=' in assignment to '{name}'")
            self.synchronize()
            return None
        
        self.expect(TokenType.SEMICOLON, error_msg="Expected ';' after assignment")
        
        return Assignment(name, value, line)
    
    # ─────────────────────────────────────────────────────────────
    #  GRAMMAR RULE: if_statement -> "if" "(" expression ")" block else_part
    #  else_part -> "else" block | ε
    # ─────────────────────────────────────────────────────────────
    
    def parse_if_statement(self) -> IfStatement:
        """
        Parse an if/if-else statement.
        Example: if (x > 10) { ... } else { ... }
        """
        if_token = self.advance()  # consume 'if'
        line = if_token.line
        
        # Expect opening parenthesis for condition
        self.expect(TokenType.LPAREN, error_msg="Expected '(' after 'if'")
        
        # Parse condition expression
        condition = self.parse_expression()
        if condition is None:
            self.add_error("Expected condition expression in 'if' statement")
            self.synchronize()
            return None
        
        # Expect closing parenthesis
        self.expect(TokenType.RPAREN, error_msg="Expected ')' after if condition")
        
        # Parse the then-block
        then_block = self.parse_block()
        if then_block is None:
            return None
        
        # Check for optional else part
        else_block = None
        if self.match(TokenType.KEYWORD, "else"):
            self.advance()  # consume 'else'
            else_block = self.parse_block()
        
        return IfStatement(condition, then_block, else_block, line)
    
    # ─────────────────────────────────────────────────────────────
    #  GRAMMAR RULE: while_statement -> "while" "(" expression ")" block
    # ─────────────────────────────────────────────────────────────
    
    def parse_while_statement(self) -> WhileStatement:
        """
        Parse a while loop.
        Example: while (x < 10) { x = x + 1; }
        """
        while_token = self.advance()  # consume 'while'
        line = while_token.line
        
        self.expect(TokenType.LPAREN, error_msg="Expected '(' after 'while'")
        
        condition = self.parse_expression()
        if condition is None:
            self.add_error("Expected condition expression in 'while' statement")
            self.synchronize()
            return None
        
        self.expect(TokenType.RPAREN, error_msg="Expected ')' after while condition")
        
        body = self.parse_block()
        if body is None:
            return None
        
        return WhileStatement(condition, body, line)
    
    # ─────────────────────────────────────────────────────────────
    #  GRAMMAR RULE: print_statement -> "print" "(" print_argument ")" ";"
    #  print_argument -> expression | STRING
    # ─────────────────────────────────────────────────────────────
    
    def parse_print_statement(self) -> PrintStatement:
        """
        Parse a print statement.
        Examples: print(x);   print("Hello");
        """
        print_token = self.advance()  # consume 'print'
        line = print_token.line
        
        self.expect(TokenType.LPAREN, error_msg="Expected '(' after 'print'")
        
        # Parse the argument (expression or string)
        argument = self.parse_expression()
        if argument is None:
            self.add_error("Expected expression or string in 'print' statement")
            self.synchronize()
            return None
        
        self.expect(TokenType.RPAREN, error_msg="Expected ')' after print argument")
        self.expect(TokenType.SEMICOLON, error_msg="Expected ';' after print statement")
        
        return PrintStatement(argument, line)
    
    # ─────────────────────────────────────────────────────────────
    #  GRAMMAR RULE: block -> "{" statement_list "}"
    # ─────────────────────────────────────────────────────────────
    
    def parse_block(self) -> Block:
        """
        Parse a block of statements enclosed in braces.
        Example: { int x = 10; print(x); }
        """
        lbrace = self.expect(TokenType.LBRACE, error_msg="Expected '{'")
        if lbrace is None:
            self.synchronize()
            return None
        line = lbrace.line
        
        # Parse statements inside the block
        statements = self.parse_statement_list()
        
        self.expect(TokenType.RBRACE, error_msg="Expected '}' to close block")
        
        return Block(statements, line)
    
    # ─────────────────────────────────────────────────────────────
    #  EXPRESSION PARSING
    #
    #  Expressions are parsed using a precedence climbing approach.
    #  Each level of the expression grammar corresponds to a
    #  different precedence level.
    #
    #  Lowest precedence at top, highest at bottom:
    #    logical_or  (||)
    #    logical_and (&&)
    #    equality    (==, !=)
    #    relational  (<, >, <=, >=)
    #    additive    (+, -)
    #    term        (*, /, %)
    #    factor      (literals, ids, parens, unary)
    # ─────────────────────────────────────────────────────────────
    
    def parse_expression(self):
        """
        Grammar: expression -> logical_or
        Entry point for expression parsing.
        """
        return self.parse_logical_or()
    
    def parse_logical_or(self):
        """
        Grammar: logical_or -> logical_and ("||" logical_and)*
        
        Lowest precedence binary operator.
        """
        left = self.parse_logical_and()
        if left is None:
            return None
        
        while self.match(TokenType.OR):
            op_token = self.advance()
            right = self.parse_logical_and()
            if right is None:
                self.add_error("Expected expression after '||'")
                return left
            left = BinaryExpression("||", left, right, op_token.line)
        
        return left
    
    def parse_logical_and(self):
        """
        Grammar: logical_and -> equality ("&&" equality)*
        """
        left = self.parse_equality()
        if left is None:
            return None
        
        while self.match(TokenType.AND):
            op_token = self.advance()
            right = self.parse_equality()
            if right is None:
                self.add_error("Expected expression after '&&'")
                return left
            left = BinaryExpression("&&", left, right, op_token.line)
        
        return left
    
    def parse_equality(self):
        """
        Grammar: equality -> relational (("==" | "!=") relational)*
        """
        left = self.parse_relational()
        if left is None:
            return None
        
        while self.match(TokenType.EQUAL) or self.match(TokenType.NOT_EQUAL):
            op_token = self.advance()
            right = self.parse_relational()
            if right is None:
                self.add_error(f"Expected expression after '{op_token.value}'")
                return left
            left = BinaryExpression(op_token.value, left, right, op_token.line)
        
        return left
    
    def parse_relational(self):
        """
        Grammar: relational -> additive (("<" | ">" | "<=" | ">=") additive)*
        """
        left = self.parse_additive()
        if left is None:
            return None
        
        while self.current_token().type in (
            TokenType.LESS, TokenType.GREATER,
            TokenType.LESS_EQ, TokenType.GREATER_EQ
        ):
            op_token = self.advance()
            right = self.parse_additive()
            if right is None:
                self.add_error(f"Expected expression after '{op_token.value}'")
                return left
            left = BinaryExpression(op_token.value, left, right, op_token.line)
        
        return left
    
    def parse_additive(self):
        """
        Grammar: additive -> term (("+" | "-") term)*
        """
        left = self.parse_term()
        if left is None:
            return None
        
        while self.match(TokenType.PLUS) or self.match(TokenType.MINUS):
            op_token = self.advance()
            right = self.parse_term()
            if right is None:
                self.add_error(f"Expected expression after '{op_token.value}'")
                return left
            left = BinaryExpression(op_token.value, left, right, op_token.line)
        
        return left
    
    def parse_term(self):
        """
        Grammar: term -> factor (("*" | "/" | "%") factor)*
        """
        left = self.parse_factor()
        if left is None:
            return None
        
        while self.current_token().type in (
            TokenType.MULTIPLY, TokenType.DIVIDE, TokenType.MODULO
        ):
            op_token = self.advance()
            right = self.parse_factor()
            if right is None:
                self.add_error(f"Expected expression after '{op_token.value}'")
                return left
            left = BinaryExpression(op_token.value, left, right, op_token.line)
        
        return left
    
    def parse_factor(self):
        """
        Grammar: factor -> NUMBER | STRING | ID | "true" | "false"
                         | "(" expression ")" | "!" factor | "-" factor
        
        This is the highest precedence level — the "atoms" of expressions.
        """
        token = self.current_token()
        
        # Number literal
        if token.type == TokenType.NUMBER:
            self.advance()
            return Literal(token.value, "NUMBER", token.line)
        
        # String literal
        if token.type == TokenType.STRING:
            self.advance()
            return Literal(token.value, "STRING", token.line)
        
        # Boolean literal (true / false)
        if token.type == TokenType.BOOLEAN:
            self.advance()
            return Literal(token.value, "BOOLEAN", token.line)
        
        # Identifier (variable reference)
        if token.type == TokenType.ID:
            self.advance()
            return Identifier(token.value, token.line)
        
        # Parenthesized expression: ( expression )
        if token.type == TokenType.LPAREN:
            self.advance()  # consume '('
            expr = self.parse_expression()
            if expr is None:
                self.add_error("Expected expression after '('")
                return None
            self.expect(TokenType.RPAREN, error_msg="Expected ')' after expression")
            return expr
        
        # Unary NOT: !factor
        if token.type == TokenType.NOT:
            self.advance()
            operand = self.parse_factor()
            if operand is None:
                self.add_error("Expected expression after '!'")
                return None
            return UnaryExpression("!", operand, token.line)
        
        # Unary minus: -factor
        if token.type == TokenType.MINUS:
            self.advance()
            operand = self.parse_factor()
            if operand is None:
                self.add_error("Expected expression after '-'")
                return None
            return UnaryExpression("-", operand, token.line)
        
        # ── Error: unexpected token in expression ──
        if token.type != TokenType.EOF:
            self.add_error(
                f"Unexpected token '{token.value}' in expression. "
                f"Expected a number, identifier, string, or '('"
            )
        else:
            self.add_error("Unexpected end of input. Expected an expression")
        
        return None
