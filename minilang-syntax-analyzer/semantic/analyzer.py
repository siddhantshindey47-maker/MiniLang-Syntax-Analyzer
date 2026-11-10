"""Semantic analysis for MiniLang.

Checks identifiers, scopes, declarations, assignments, expression types,
and boolean conditions after parsing has produced an AST.
"""

from dataclasses import dataclass
from typing import Optional

from parser.ast_nodes import (
    Program, Declaration, Assignment, IfStatement, WhileStatement,
    PrintStatement, Block, BinaryExpression, UnaryExpression, Literal,
    Identifier,
)


@dataclass
class SemanticError:
    message: str
    line: int
    column: int = 1
    kind: str = "Semantic Error"

    def to_dict(self) -> dict:
        return {
            "message": self.message,
            "line": self.line,
            "column": self.column,
            "kind": self.kind,
        }


@dataclass
class Symbol:
    name: str
    var_type: str
    scope: str
    line: int
    initialized: bool = False

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "type": self.var_type,
            "scope": self.scope,
            "line": self.line,
            "initialized": self.initialized,
        }


class SemanticAnalyzer:
    """Walk the AST and perform semantic checks with lexical scoping."""

    NUMERIC_TYPES = {"int", "float"}
    VALID_TYPES = {"int", "float", "bool"}

    def __init__(self):
        self.errors: list[SemanticError] = []
        self.scopes: list[dict[str, Symbol]] = []
        self.scope_names: list[str] = []
        self.all_symbols: list[Symbol] = []
        self._next_scope_id = 0

    def analyze(self, program: Optional[Program]):
        self.errors = []
        self.scopes = []
        self.scope_names = []
        self.all_symbols = []
        self._next_scope_id = 0

        if program is None:
            return [], []

        self._enter_scope("global")
        for statement in program.statements:
            self.visit(statement)
        self._exit_scope()
        return self.errors, self.all_symbols

    # ----- Scope management -----
    def _enter_scope(self, requested_name: str | None = None):
        if requested_name and not self.scope_names:
            name = requested_name
        else:
            self._next_scope_id += 1
            name = f"block_{self._next_scope_id}"
        self.scopes.append({})
        self.scope_names.append(name)

    def _exit_scope(self):
        if self.scopes:
            self.scopes.pop()
            self.scope_names.pop()

    @property
    def current_scope(self):
        return self.scopes[-1]

    @property
    def current_scope_name(self):
        return self.scope_names[-1]

    def _lookup(self, name: str) -> Optional[Symbol]:
        for scope in reversed(self.scopes):
            if name in scope:
                return scope[name]
        return None

    def _lookup_current(self, name: str) -> Optional[Symbol]:
        return self.current_scope.get(name)

    def _error(self, message: str, node, column: int = 1):
        line = getattr(node, "line", 0) or 0
        self.errors.append(SemanticError(message, line, column))

    # ----- AST visitors -----
    def visit(self, node):
        if node is None:
            return None
        method = getattr(self, f"visit_{node.__class__.__name__}", None)
        if method is None:
            return None
        return method(node)

    def visit_Program(self, node: Program):
        for statement in node.statements:
            self.visit(statement)

    def visit_Block(self, node: Block):
        self._enter_scope()
        for statement in node.statements:
            self.visit(statement)
        self._exit_scope()

    def visit_Declaration(self, node: Declaration):
        if node.var_type not in self.VALID_TYPES:
            self._error(f"Unknown type '{node.var_type}' for variable '{node.name}'.", node)
            return

        if self._lookup_current(node.name):
            self._error(
                f"Variable '{node.name}' is already declared in the current scope.",
                node,
            )
            # Still analyze the initializer for additional useful errors.
            if node.value:
                self.visit(node.value)
            return

        symbol = Symbol(
            name=node.name,
            var_type=node.var_type,
            scope=self.current_scope_name,
            line=node.line,
            initialized=node.value is not None,
        )
        self.current_scope[node.name] = symbol
        self.all_symbols.append(symbol)

        if node.value is not None:
            actual = self.visit(node.value)
            if actual and not self.is_assignable(node.var_type, actual):
                self._error(
                    f"Type mismatch: cannot assign {self.pretty_type(actual)} "
                    f"to variable '{node.name}' of type {node.var_type}.",
                    node,
                )

    def visit_Assignment(self, node: Assignment):
        symbol = self._lookup(node.name)
        if symbol is None:
            self._error(f"Variable '{node.name}' is not declared.", node)
            self.visit(node.value)
            return

        actual = self.visit(node.value)
        if actual and not self.is_assignable(symbol.var_type, actual):
            self._error(
                f"Type mismatch: cannot assign {self.pretty_type(actual)} "
                f"to variable '{node.name}' of type {symbol.var_type}.",
                node,
            )
        symbol.initialized = True

    def visit_IfStatement(self, node: IfStatement):
        condition_type = self.visit(node.condition)
        self._require_boolean(condition_type, "if condition", node)
        self.visit(node.then_block)
        if node.else_block:
            self.visit(node.else_block)

    def visit_WhileStatement(self, node: WhileStatement):
        condition_type = self.visit(node.condition)
        self._require_boolean(condition_type, "while condition", node)
        self.visit(node.body)

    def visit_PrintStatement(self, node: PrintStatement):
        self.visit(node.argument)

    # ----- Expressions -----
    def visit_Identifier(self, node: Identifier):
        symbol = self._lookup(node.name)
        if symbol is None:
            self._error(f"Variable '{node.name}' is not declared.", node)
            return None
        return symbol.var_type

    def visit_Literal(self, node: Literal):
        if node.literal_type == "BOOLEAN":
            return "bool"
        if node.literal_type == "STRING":
            return "string"
        # NUMBER stores the original token text, so distinguish integers/floats.
        value = str(node.value)
        return "float" if "." in value else "int"

    def visit_UnaryExpression(self, node: UnaryExpression):
        operand_type = self.visit(node.operand)
        if operand_type is None:
            return None

        if node.operator == "-":
            if operand_type not in self.NUMERIC_TYPES:
                self._error(
                    f"Unary '-' requires a numeric operand, got {self.pretty_type(operand_type)}.",
                    node,
                )
                return None
            return operand_type

        if node.operator == "!":
            if operand_type != "bool":
                self._error(
                    f"Logical '!' requires a boolean operand, got {self.pretty_type(operand_type)}.",
                    node,
                )
                return None
            return "bool"

        return None

    def visit_BinaryExpression(self, node: BinaryExpression):
        left = self.visit(node.left)
        right = self.visit(node.right)
        if left is None or right is None:
            return None

        op = node.operator

        if op in {"+", "-", "*", "/", "%"}:
            if left not in self.NUMERIC_TYPES or right not in self.NUMERIC_TYPES:
                self._error(
                    f"Operator '{op}' requires numeric operands, got "
                    f"{self.pretty_type(left)} and {self.pretty_type(right)}.",
                    node,
                )
                return None
            # Division and mixed numeric expressions produce float.
            return "float" if op == "/" or "float" in {left, right} else "int"

        if op in {"<", ">", "<=", ">="}:
            if left not in self.NUMERIC_TYPES or right not in self.NUMERIC_TYPES:
                self._error(
                    f"Comparison '{op}' requires numeric operands, got "
                    f"{self.pretty_type(left)} and {self.pretty_type(right)}.",
                    node,
                )
            return "bool"

        if op in {"==", "!="}:
            compatible = (
                left == right
                or left in self.NUMERIC_TYPES and right in self.NUMERIC_TYPES
            )
            if not compatible:
                self._error(
                    f"Cannot compare {self.pretty_type(left)} with {self.pretty_type(right)} using '{op}'.",
                    node,
                )
            return "bool"

        if op in {"&&", "||"}:
            if left != "bool" or right != "bool":
                self._error(
                    f"Logical operator '{op}' requires boolean operands, got "
                    f"{self.pretty_type(left)} and {self.pretty_type(right)}.",
                    node,
                )
            return "bool"

        return None

    def _require_boolean(self, actual_type, context: str, node):
        if actual_type is not None and actual_type != "bool":
            self._error(
                f"{context.capitalize()} must be boolean, got {self.pretty_type(actual_type)}.",
                node,
            )

    @staticmethod
    def pretty_type(type_name: str) -> str:
        return type_name.upper() if type_name else "UNKNOWN"

    @staticmethod
    def is_assignable(expected: str, actual: str) -> bool:
        if expected == actual:
            return True
        # MiniLang permits widening int -> float.
        return expected == "float" and actual == "int"
