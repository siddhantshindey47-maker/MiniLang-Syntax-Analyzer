"""
test_lexer.py — Tests for the MiniLang Lexical Analyzer
========================================================
Run with: python -m pytest tests/test_lexer.py -v
Or:       python tests/test_lexer.py
"""

import sys
import os

# Add project root to path so imports work
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lexer import Lexer, TokenType
from tests.test_cases import VALID_CASES


def test_simple_declaration():
    """Test tokenizing: int x;"""
    lexer = Lexer("int x;")
    tokens, errors = lexer.tokenize()
    
    assert len(errors) == 0, f"Expected no errors, got: {errors}"
    assert tokens[0].type == TokenType.KEYWORD and tokens[0].value == "int"
    assert tokens[1].type == TokenType.ID and tokens[1].value == "x"
    assert tokens[2].type == TokenType.SEMICOLON
    assert tokens[3].type == TokenType.EOF
    print("[PASS] test_simple_declaration")


def test_declaration_with_init():
    """Test tokenizing: int x = 10;"""
    lexer = Lexer("int x = 10;")
    tokens, errors = lexer.tokenize()
    
    assert len(errors) == 0
    assert tokens[0].value == "int"
    assert tokens[1].value == "x"
    assert tokens[2].type == TokenType.ASSIGN
    assert tokens[3].type == TokenType.NUMBER and tokens[3].value == "10"
    assert tokens[4].type == TokenType.SEMICOLON
    print("[PASS] test_declaration_with_init")


def test_float_number():
    """Test tokenizing float literals."""
    lexer = Lexer("float pi = 3.14;")
    tokens, errors = lexer.tokenize()
    
    assert len(errors) == 0
    assert tokens[3].type == TokenType.NUMBER
    assert tokens[3].value == "3.14"
    print("[PASS] test_float_number")


def test_string_literal():
    """Test tokenizing string literals."""
    lexer = Lexer('print("Hello World");')
    tokens, errors = lexer.tokenize()
    
    assert len(errors) == 0
    assert tokens[2].type == TokenType.STRING
    assert tokens[2].value == "Hello World"
    print("[PASS] test_string_literal")


def test_operators():
    """Test all operator tokens."""
    lexer = Lexer("+ - * / % = == != < > <= >= && || !")
    tokens, errors = lexer.tokenize()
    
    assert len(errors) == 0
    expected_types = [
        TokenType.PLUS, TokenType.MINUS, TokenType.MULTIPLY,
        TokenType.DIVIDE, TokenType.MODULO, TokenType.ASSIGN,
        TokenType.EQUAL, TokenType.NOT_EQUAL,
        TokenType.LESS, TokenType.GREATER,
        TokenType.LESS_EQ, TokenType.GREATER_EQ,
        TokenType.AND, TokenType.OR, TokenType.NOT,
        TokenType.EOF
    ]
    for i, expected in enumerate(expected_types):
        assert tokens[i].type == expected, f"Token {i}: expected {expected}, got {tokens[i].type}"
    print("[PASS] test_operators")


def test_keywords():
    """Test all keyword tokens."""
    lexer = Lexer("int float bool if else while print")
    tokens, errors = lexer.tokenize()
    
    assert len(errors) == 0
    for i in range(7):
        assert tokens[i].type == TokenType.KEYWORD
    print("[PASS] test_keywords")


def test_boolean_literals():
    """Test true and false as BOOLEAN tokens."""
    lexer = Lexer("true false")
    tokens, errors = lexer.tokenize()
    
    assert len(errors) == 0
    assert tokens[0].type == TokenType.BOOLEAN and tokens[0].value == "true"
    assert tokens[1].type == TokenType.BOOLEAN and tokens[1].value == "false"
    print("[PASS] test_boolean_literals")


def test_comments_are_skipped():
    """Test that comments are ignored."""
    lexer = Lexer("int x; // this is a comment\nint y;")
    tokens, errors = lexer.tokenize()
    
    assert len(errors) == 0
    values = [t.value for t in tokens if t.type != TokenType.EOF]
    assert "this" not in values
    assert "comment" not in values
    print("[PASS] test_comments_are_skipped")


def test_line_column_tracking():
    """Test that line and column numbers are correct."""
    lexer = Lexer("int x;\nint y;")
    tokens, errors = lexer.tokenize()
    
    assert len(errors) == 0
    assert tokens[0].line == 1 and tokens[0].column == 1
    assert tokens[1].line == 1 and tokens[1].column == 5
    assert tokens[3].line == 2 and tokens[3].column == 1
    assert tokens[4].line == 2 and tokens[4].column == 5
    print("[PASS] test_line_column_tracking")


def test_separators():
    """Test separator tokens."""
    lexer = Lexer("( ) { } ;")
    tokens, errors = lexer.tokenize()
    
    assert len(errors) == 0
    expected = [TokenType.LPAREN, TokenType.RPAREN, TokenType.LBRACE,
                TokenType.RBRACE, TokenType.SEMICOLON, TokenType.EOF]
    for i, exp in enumerate(expected):
        assert tokens[i].type == exp
    print("[PASS] test_separators")


def test_unexpected_character():
    """Test that unexpected characters produce errors."""
    lexer = Lexer("int x = @;")
    tokens, errors = lexer.tokenize()
    
    assert len(errors) > 0
    assert "@" in errors[0].message
    print("[PASS] test_unexpected_character")


def test_unterminated_string():
    """Test that unterminated strings produce errors."""
    lexer = Lexer('print("Hello)')
    tokens, errors = lexer.tokenize()
    
    assert len(errors) > 0
    print("[PASS] test_unterminated_string")


def test_all_valid_programs_tokenize():
    """Test that all valid programs tokenize without errors."""
    for name, code in VALID_CASES.items():
        lexer = Lexer(code)
        tokens, errors = lexer.tokenize()
        assert len(errors) == 0, f"Lexer errors in '{name}': {[e.message for e in errors]}"
    print(f"[PASS] test_all_valid_programs_tokenize ({len(VALID_CASES)} programs)")


# ─── Run all tests ───
if __name__ == "__main__":
    print("=" * 50)
    print("  MiniLang Lexer Tests")
    print("=" * 50)
    
    tests = [
        test_simple_declaration,
        test_declaration_with_init,
        test_float_number,
        test_string_literal,
        test_operators,
        test_keywords,
        test_boolean_literals,
        test_comments_are_skipped,
        test_line_column_tracking,
        test_separators,
        test_unexpected_character,
        test_unterminated_string,
        test_all_valid_programs_tokenize,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            passed += 1
        except AssertionError as e:
            print(f"[FAIL] {test.__name__}: {e}")
            failed += 1
        except Exception as e:
            print(f"[ERROR] {test.__name__}: {e}")
            failed += 1
    
    print("=" * 50)
    print(f"  Results: {passed} passed, {failed} failed, {len(tests)} total")
    print("=" * 50)
    if failed > 0:
        sys.exit(1)
