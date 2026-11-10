"""Three-address code generation for MiniLang AST."""

from parser.ast_nodes import (
    Program, Declaration, Assignment, IfStatement, WhileStatement,
    PrintStatement, Block, BinaryExpression, UnaryExpression,
    Literal, Identifier,
)


class ThreeAddressCodeGenerator:
    """Generate readable three-address code from the existing MiniLang AST."""

    def __init__(self):
        self.instructions = []
        self.temp_counter = 0
        self.label_counter = 0

    def generate(self, program):
        self.instructions = []
        self.temp_counter = 0
        self.label_counter = 0
        if program:
            self.visit(program)
        return self.instructions

    def new_temp(self):
        self.temp_counter += 1
        return f"t{self.temp_counter}"

    def new_label(self):
        self.label_counter += 1
        return f"L{self.label_counter}"

    def emit(self, code, kind="instruction"):
        self.instructions.append({
            "line": len(self.instructions) + 1,
            "code": code,
            "kind": kind,
        })

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
        for statement in node.statements:
            self.visit(statement)

    def visit_Declaration(self, node: Declaration):
        if node.value is not None:
            value = self.visit(node.value)
            self.emit(f"{node.name} = {value}", "assignment")
        else:
            self.emit(f"{node.name} = 0", "declaration")

    def visit_Assignment(self, node: Assignment):
        value = self.visit(node.value)
        self.emit(f"{node.name} = {value}", "assignment")

    def visit_PrintStatement(self, node: PrintStatement):
        value = self.visit(node.argument)
        self.emit(f"print {value}", "io")

    def visit_IfStatement(self, node: IfStatement):
        condition = self.visit(node.condition)
        else_label = self.new_label()
        end_label = self.new_label()
        self.emit(f"ifFalse {condition} goto {else_label}", "branch")
        self.visit(node.then_block)
        if node.else_block is not None:
            self.emit(f"goto {end_label}", "branch")
            self.emit(f"{else_label}:", "label")
            self.visit(node.else_block)
            self.emit(f"{end_label}:", "label")
        else:
            self.emit(f"{else_label}:", "label")

    def visit_WhileStatement(self, node: WhileStatement):
        start_label = self.new_label()
        end_label = self.new_label()
        self.emit(f"{start_label}:", "label")
        condition = self.visit(node.condition)
        self.emit(f"ifFalse {condition} goto {end_label}", "branch")
        self.visit(node.body)
        self.emit(f"goto {start_label}", "branch")
        self.emit(f"{end_label}:", "label")

    def visit_BinaryExpression(self, node: BinaryExpression):
        left = self.visit(node.left)
        right = self.visit(node.right)
        temp = self.new_temp()
        self.emit(f"{temp} = {left} {node.operator} {right}", "expression")
        return temp

    def visit_UnaryExpression(self, node: UnaryExpression):
        operand = self.visit(node.operand)
        temp = self.new_temp()
        self.emit(f"{temp} = {node.operator}{operand}", "expression")
        return temp

    def visit_Identifier(self, node: Identifier):
        return node.name

    def visit_Literal(self, node: Literal):
        if node.literal_type == "STRING":
            return f'"{node.value}"'
        return str(node.value).lower() if node.literal_type == "BOOLEAN" else str(node.value)
