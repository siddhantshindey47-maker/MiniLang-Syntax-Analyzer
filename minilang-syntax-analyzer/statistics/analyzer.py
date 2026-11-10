"""Collect useful statistics from MiniLang tokens and AST."""

from parser.ast_nodes import (
    Program, Declaration, Assignment, IfStatement, WhileStatement,
    PrintStatement, Block, BinaryExpression, UnaryExpression,
    Literal, Identifier,
)


class CompilerStatistics:
    def calculate(self, program=None, tokens=None, semantic_errors=None, syntax_errors=None):
        counts = {
            "tokens": len(tokens or []),
            "ast_nodes": 0,
            "declarations": 0,
            "assignments": 0,
            "expressions": 0,
            "identifiers": 0,
            "literals": 0,
            "if_statements": 0,
            "while_statements": 0,
            "print_statements": 0,
            "blocks": 0,
            "semantic_errors": len(semantic_errors or []),
            "syntax_errors": len(syntax_errors or []),
        }

        if program:
            self._walk(program, counts)

        return counts

    def _walk(self, node, counts):
        if node is None:
            return
        counts["ast_nodes"] += 1

        if isinstance(node, Declaration):
            counts["declarations"] += 1
            self._walk(node.value, counts)
        elif isinstance(node, Assignment):
            counts["assignments"] += 1
            self._walk(node.value, counts)
        elif isinstance(node, IfStatement):
            counts["if_statements"] += 1
            self._walk(node.condition, counts)
            self._walk(node.then_block, counts)
            self._walk(node.else_block, counts)
        elif isinstance(node, WhileStatement):
            counts["while_statements"] += 1
            self._walk(node.condition, counts)
            self._walk(node.body, counts)
        elif isinstance(node, PrintStatement):
            counts["print_statements"] += 1
            self._walk(node.argument, counts)
        elif isinstance(node, Block):
            counts["blocks"] += 1
            for statement in node.statements:
                self._walk(statement, counts)
        elif isinstance(node, BinaryExpression):
            counts["expressions"] += 1
            self._walk(node.left, counts)
            self._walk(node.right, counts)
        elif isinstance(node, UnaryExpression):
            counts["expressions"] += 1
            self._walk(node.operand, counts)
        elif isinstance(node, Identifier):
            counts["identifiers"] += 1
        elif isinstance(node, Literal):
            counts["literals"] += 1
        elif isinstance(node, Program):
            for statement in node.statements:
                self._walk(statement, counts)
