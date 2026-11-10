"""
test_parser.py — Tests for the MiniLang Recursive Descent Parser
=================================================================
Run with: python -m pytest tests/test_parser.py -v
Or:       python tests/test_parser.py
"""

import sys
import os

# Add project root to path so imports work
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lexer import Lexer
from parser import Parser
from tests.test_cases import VALID_CASES, INVALID_CASES


def parse_code(code: str):
    """Helper: Lex and parse a string, return (ast, errors)."""
    lexer = Lexer(code)
    tokens, lexer_errors = lexer.tokenize()
    parser = Parser(tokens)
    ast, parser_errors = parser.parse()
    all_errors = lexer_errors + parser_errors
    return ast, all_errors


def test_simple_declaration():
    """Test: int x;"""
    ast, errors = parse_code("int x;")
    assert len(errors) == 0, f"Errors: {errors}"
    assert ast.to_dict()["type"] == "Program"
    assert len(ast.statements) == 1
    assert ast.statements[0].to_dict()["type"] == "Declaration"
    assert ast.statements[0].var_type == "int"
    assert ast.statements[0].name == "x"
    print("[PASS] test_simple_declaration")


def test_declaration_with_init():
    """Test: int x = 10;"""
    ast, errors = parse_code("int x = 10;")
    assert len(errors) == 0, f"Errors: {errors}"
    decl = ast.statements[0]
    assert decl.var_type == "int"
    assert decl.name == "x"
    assert decl.value is not None
    assert decl.value.to_dict()["type"] == "Literal"
    assert decl.value.value == "10"
    print("[PASS] test_declaration_with_init")


def test_assignment():
    """Test: x = 10;"""
    ast, errors = parse_code("int x = 0;\nx = 10;")
    assert len(errors) == 0, f"Errors: {errors}"
    assign = ast.statements[1]
    assert assign.to_dict()["type"] == "Assignment"
    assert assign.name == "x"
    print("[PASS] test_assignment")


def test_arithmetic_precedence():
    """Test: int x = 10 + 20 * 2;  (should give + at top, * below)"""
    ast, errors = parse_code("int x = 10 + 20 * 2;")
    assert len(errors) == 0, f"Errors: {errors}"
    expr = ast.statements[0].value
    # Top-level should be + (addition)
    assert expr.to_dict()["type"] == "BinaryExpression"
    assert expr.operator == "+"
    # Right child should be * (multiplication)
    assert expr.right.operator == "*"
    print("[PASS] test_arithmetic_precedence")


def test_parentheses():
    """Test: int x = (10 + 20) * 2;  (parentheses change precedence)"""
    ast, errors = parse_code("int x = (10 + 20) * 2;")
    assert len(errors) == 0, f"Errors: {errors}"
    expr = ast.statements[0].value
    # Top-level should be * (multiplication)
    assert expr.operator == "*"
    # Left child should be + (addition, from parentheses)
    assert expr.left.operator == "+"
    print("[PASS] test_parentheses")


def test_if_statement():
    """Test if statement."""
    ast, errors = parse_code("int x = 10;\nif (x > 5) {\n    print(x);\n}")
    assert len(errors) == 0, f"Errors: {errors}"
    if_stmt = ast.statements[1]
    assert if_stmt.to_dict()["type"] == "IfStatement"
    assert if_stmt.condition is not None
    assert if_stmt.then_block is not None
    assert if_stmt.else_block is None
    print("[PASS] test_if_statement")


def test_if_else():
    """Test if-else statement."""
    code = 'if (true) {\n    print("yes");\n} else {\n    print("no");\n}'
    ast, errors = parse_code(code)
    assert len(errors) == 0, f"Errors: {errors}"
    if_stmt = ast.statements[0]
    assert if_stmt.else_block is not None
    print("[PASS] test_if_else")


def test_while_loop():
    """Test while loop."""
    code = "int x = 0;\nwhile (x < 10) {\n    x = x + 1;\n}"
    ast, errors = parse_code(code)
    assert len(errors) == 0, f"Errors: {errors}"
    while_stmt = ast.statements[1]
    assert while_stmt.to_dict()["type"] == "WhileStatement"
    print("[PASS] test_while_loop")


def test_print_string():
    """Test print with string."""
    ast, errors = parse_code('print("Hello");')
    assert len(errors) == 0, f"Errors: {errors}"
    print_stmt = ast.statements[0]
    assert print_stmt.to_dict()["type"] == "PrintStatement"
    assert print_stmt.argument.to_dict()["literal_type"] == "STRING"
    print("[PASS] test_print_string")


def test_print_expression():
    """Test print with expression."""
    ast, errors = parse_code("int x = 5;\nprint(x + 1);")
    assert len(errors) == 0, f"Errors: {errors}"
    print("[PASS] test_print_expression")


def test_logical_operators():
    """Test logical AND, OR, NOT."""
    ast, errors = parse_code("bool r = true && false || !true;")
    assert len(errors) == 0, f"Errors: {errors}"
    print("[PASS] test_logical_operators")


def test_unary_minus():
    """Test unary minus."""
    ast, errors = parse_code("int x = -10;")
    assert len(errors) == 0, f"Errors: {errors}"
    expr = ast.statements[0].value
    assert expr.to_dict()["type"] == "UnaryExpression"
    assert expr.operator == "-"
    print("[PASS] test_unary_minus")


def test_nested_blocks():
    """Test nested blocks and statements."""
    code = """if (true) {
    if (false) {
        print("inner");
    }
    print("outer");
}"""
    ast, errors = parse_code(code)
    assert len(errors) == 0, f"Errors: {errors}"
    print("[PASS] test_nested_blocks")


def test_block():
    """Test standalone block."""
    code = "{\n    int x = 10;\n    print(x);\n}"
    ast, errors = parse_code(code)
    assert len(errors) == 0, f"Errors: {errors}"
    print("[PASS] test_block")


def test_ast_tree_string():
    """Test that tree string generation works."""
    ast, errors = parse_code("int x = 10 + 20;")
    assert len(errors) == 0, f"Errors: {errors}"
    tree = ast.tree_string()
    assert "Program" in tree
    assert "Declaration" in tree
    assert "BinaryOp" in tree
    print("[PASS] test_ast_tree_string")


def test_complex_expression():
    """Test complex expression with multiple operators."""
    code = "int r = (10 + 20) * (30 - 5) / 2 % 7;"
    ast, errors = parse_code(code)
    assert len(errors) == 0, f"Errors: {errors}"
    print("[PASS] test_complex_expression")


# ─── Error Detection Tests ──────────────────────────────

def test_error_missing_semicolon():
    """Error test: int x = 10  (missing ;)"""
    ast, errors = parse_code("int x = 10")
    assert len(errors) > 0, "Expected error for missing semicolon"
    print("[PASS] test_error_missing_semicolon")


def test_error_missing_expression():
    """Error test: x = 10 + ;  (missing operand)"""
    ast, errors = parse_code("int x = 10;\nx = 10 + ;")
    assert len(errors) > 0, "Expected error for missing expression"
    print("[PASS] test_error_missing_expression")


def test_error_missing_close_paren():
    """Error test: if (x > 10 {  (missing ))"""
    ast, errors = parse_code("int x = 10;\nif (x > 10 {\n    print(x);\n}")
    assert len(errors) > 0, "Expected error for missing close paren"
    print("[PASS] test_error_missing_close_paren")


def test_error_missing_close_brace():
    """Error test: missing }"""
    ast, errors = parse_code("if (true) {\n    print(1);")
    assert len(errors) > 0, "Expected error for missing close brace"
    print("[PASS] test_error_missing_close_brace")


def test_error_empty_assignment():
    """Error test: x = ;"""
    ast, errors = parse_code("int x = 0;\nx = ;")
    assert len(errors) > 0, "Expected error for empty assignment"
    print("[PASS] test_error_empty_assignment")


def test_all_valid_programs_parse():
    """Test that all valid programs parse without errors."""
    for name, code in VALID_CASES.items():
        ast, errors = parse_code(code)
        assert len(errors) == 0, f"Parse errors in '{name}': {[str(e) for e in errors]}"
    print(f"[PASS] test_all_valid_programs_parse ({len(VALID_CASES)} programs)")


def test_all_invalid_programs_detect_errors():
    """Test that all invalid programs produce at least one error."""
    for name, case in INVALID_CASES.items():
        ast, errors = parse_code(case["code"])
        assert len(errors) > 0, f"Expected errors for '{name}' ({case['description']}) but got none"
    print(f"[PASS] test_all_invalid_programs_detect_errors ({len(INVALID_CASES)} programs)")


# ─── Run all tests ───
if __name__ == "__main__":
    print("=" * 50)
    print("  MiniLang Parser Tests")
    print("=" * 50)
    
    tests = [
        test_simple_declaration,
        test_declaration_with_init,
        test_assignment,
        test_arithmetic_precedence,
        test_parentheses,
        test_if_statement,
        test_if_else,
        test_while_loop,
        test_print_string,
        test_print_expression,
        test_logical_operators,
        test_unary_minus,
        test_nested_blocks,
        test_block,
        test_ast_tree_string,
        test_complex_expression,
        test_error_missing_semicolon,
        test_error_missing_expression,
        test_error_missing_close_paren,
        test_error_missing_close_brace,
        test_error_empty_assignment,
        test_all_valid_programs_parse,
        test_all_invalid_programs_detect_errors,
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
