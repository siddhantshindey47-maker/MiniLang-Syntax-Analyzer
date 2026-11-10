import unittest

from lexer import Lexer
from parser import Parser
from semantic import SemanticAnalyzer


def analyze(code):
    lexer = Lexer(code)
    tokens, lexer_errors = lexer.tokenize()
    if lexer_errors:
        return lexer_errors, []
    parser = Parser(tokens)
    ast, parser_errors = parser.parse()
    if parser_errors:
        return parser_errors, []
    return SemanticAnalyzer().analyze(ast)


class SemanticAnalyzerTests(unittest.TestCase):
    def test_valid_program(self):
        errors, symbols = analyze("int x = 10; float y = x + 2.5; bool ok = x < y; print(ok);")
        self.assertEqual(errors, [])
        self.assertEqual([s.name for s in symbols], ["x", "y", "ok"])

    def test_undeclared_variable(self):
        errors, _ = analyze("x = 10;")
        self.assertTrue(any("not declared" in e.message for e in errors))

    def test_duplicate_declaration(self):
        errors, _ = analyze("int x = 1; int x = 2;")
        self.assertTrue(any("already declared" in e.message for e in errors))

    def test_type_mismatch(self):
        errors, _ = analyze("int x = true;")
        self.assertTrue(any("Type mismatch" in e.message for e in errors))

    def test_condition_must_be_boolean(self):
        errors, _ = analyze("int x = 1; if (x) { print(x); }")
        self.assertTrue(any("must be boolean" in e.message for e in errors))

    def test_logical_operator_types(self):
        errors, _ = analyze("bool x = true && 1;")
        self.assertTrue(any("requires boolean operands" in e.message for e in errors))

    def test_nested_scope_can_shadow(self):
        errors, symbols = analyze("int x = 1; if (true) { float x = 2.5; print(x); } print(x);")
        self.assertEqual(errors, [])
        self.assertEqual([s.scope for s in symbols], ["global", "block_1"])


if __name__ == "__main__":
    unittest.main()
