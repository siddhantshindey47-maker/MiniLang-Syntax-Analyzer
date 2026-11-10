"""
ast.py - Abstract Syntax Tree Node Definitions for MiniLang
============================================================

An AST (Abstract Syntax Tree) is a tree representation of the syntactic
structure of source code. Each node in the tree represents a construct
in the source code.

Key difference from a Parse Tree:
  - A Parse Tree contains every grammar symbol (including terminals).
  - An AST contains only the meaningful structure, omitting punctuation
    like parentheses and semicolons.

Example:
  Source: x = 10 + 20 * 2;
  
  AST:
    Assignment
    ├── Identifier(x)
    └── BinaryOp(+)
        ├── Number(10)
        └── BinaryOp(*)
            ├── Number(20)
            └── Number(2)

Each AST node class below corresponds to a language construct.
"""


class ASTNode:
    """
    Base class for all AST nodes.
    Every node can convert itself to a dictionary (for JSON)
    and to a readable tree string (for display).
    """
    
    def to_dict(self) -> dict:
        """Convert node to a JSON-serializable dictionary."""
        raise NotImplementedError
    
    def tree_string(self, indent: str = "", is_last: bool = True) -> str:
        """Generate a human-readable tree representation."""
        raise NotImplementedError


class Program(ASTNode):
    """
    Root node of the AST. Contains a list of statements.
    
    Grammar: program -> statement_list
    """
    
    def __init__(self, statements: list):
        self.statements = statements
    
    def to_dict(self) -> dict:
        return {
            "type": "Program",
            "statements": [s.to_dict() for s in self.statements]
        }
    
    def tree_string(self, indent: str = "", is_last: bool = True) -> str:
        result = "Program\n"
        for i, stmt in enumerate(self.statements):
            last = (i == len(self.statements) - 1)
            result += stmt.tree_string("", last)
        return result


class Declaration(ASTNode):
    """
    Variable declaration, optionally with initialization.
    
    Grammar: declaration -> type ID declaration_init ";"
    Examples: int x;    int x = 10;
    """
    
    def __init__(self, var_type: str, name: str, value=None, line: int = 0):
        self.var_type = var_type   # "int", "float", or "bool"
        self.name = name           # variable name
        self.value = value         # initial value expression (or None)
        self.line = line
    
    def to_dict(self) -> dict:
        result = {
            "type": "Declaration",
            "var_type": self.var_type,
            "name": self.name,
        }
        if self.value:
            result["value"] = self.value.to_dict()
        return result
    
    def tree_string(self, indent: str = "", is_last: bool = True) -> str:
        connector = "└── " if is_last else "├── "
        result = indent + connector + f"Declaration ({self.var_type} {self.name})\n"
        new_indent = indent + ("    " if is_last else "│   ")
        if self.value:
            result += self.value.tree_string(new_indent, True)
        return result


class Assignment(ASTNode):
    """
    Variable assignment.
    
    Grammar: assignment -> ID "=" expression ";"
    Example: x = 10 + 5;
    """
    
    def __init__(self, name: str, value, line: int = 0):
        self.name = name     # variable name being assigned to
        self.value = value   # expression being assigned
        self.line = line
    
    def to_dict(self) -> dict:
        return {
            "type": "Assignment",
            "name": self.name,
            "value": self.value.to_dict()
        }
    
    def tree_string(self, indent: str = "", is_last: bool = True) -> str:
        connector = "└── " if is_last else "├── "
        result = indent + connector + f"Assignment ({self.name})\n"
        new_indent = indent + ("    " if is_last else "│   ")
        result += self.value.tree_string(new_indent, True)
        return result


class IfStatement(ASTNode):
    """
    If / if-else statement.
    
    Grammar: if_statement -> "if" "(" expression ")" block else_part
    """
    
    def __init__(self, condition, then_block, else_block=None, line: int = 0):
        self.condition = condition     # condition expression
        self.then_block = then_block   # block executed if condition is true
        self.else_block = else_block   # block executed if condition is false (or None)
        self.line = line
    
    def to_dict(self) -> dict:
        result = {
            "type": "IfStatement",
            "condition": self.condition.to_dict(),
            "then": self.then_block.to_dict()
        }
        if self.else_block:
            result["else"] = self.else_block.to_dict()
        return result
    
    def tree_string(self, indent: str = "", is_last: bool = True) -> str:
        connector = "└── " if is_last else "├── "
        result = indent + connector + "IfStatement\n"
        new_indent = indent + ("    " if is_last else "│   ")
        
        # Condition
        result += new_indent + "├── Condition\n"
        result += self.condition.tree_string(new_indent + "│   ", True)
        
        # Then block
        has_else = self.else_block is not None
        result += new_indent + ("├── " if has_else else "└── ") + "Then\n"
        then_indent = new_indent + ("│   " if has_else else "    ")
        result += self.then_block.tree_string(then_indent, True)
        
        # Else block
        if self.else_block:
            result += new_indent + "└── Else\n"
            result += self.else_block.tree_string(new_indent + "    ", True)
        
        return result


class WhileStatement(ASTNode):
    """
    While loop.
    
    Grammar: while_statement -> "while" "(" expression ")" block
    """
    
    def __init__(self, condition, body, line: int = 0):
        self.condition = condition   # loop condition
        self.body = body             # loop body block
        self.line = line
    
    def to_dict(self) -> dict:
        return {
            "type": "WhileStatement",
            "condition": self.condition.to_dict(),
            "body": self.body.to_dict()
        }
    
    def tree_string(self, indent: str = "", is_last: bool = True) -> str:
        connector = "└── " if is_last else "├── "
        result = indent + connector + "WhileStatement\n"
        new_indent = indent + ("    " if is_last else "│   ")
        
        result += new_indent + "├── Condition\n"
        result += self.condition.tree_string(new_indent + "│   ", True)
        result += new_indent + "└── Body\n"
        result += self.body.tree_string(new_indent + "    ", True)
        
        return result


class PrintStatement(ASTNode):
    """
    Print statement.
    
    Grammar: print_statement -> "print" "(" print_argument ")" ";"
    """
    
    def __init__(self, argument, line: int = 0):
        self.argument = argument   # expression or string to print
        self.line = line
    
    def to_dict(self) -> dict:
        return {
            "type": "PrintStatement",
            "argument": self.argument.to_dict()
        }
    
    def tree_string(self, indent: str = "", is_last: bool = True) -> str:
        connector = "└── " if is_last else "├── "
        result = indent + connector + "PrintStatement\n"
        new_indent = indent + ("    " if is_last else "│   ")
        result += self.argument.tree_string(new_indent, True)
        return result


class Block(ASTNode):
    """
    A block of statements enclosed in braces.
    
    Grammar: block -> "{" statement_list "}"
    """
    
    def __init__(self, statements: list, line: int = 0):
        self.statements = statements
        self.line = line
    
    def to_dict(self) -> dict:
        return {
            "type": "Block",
            "statements": [s.to_dict() for s in self.statements]
        }
    
    def tree_string(self, indent: str = "", is_last: bool = True) -> str:
        connector = "└── " if is_last else "├── "
        result = indent + connector + "Block\n"
        new_indent = indent + ("    " if is_last else "│   ")
        for i, stmt in enumerate(self.statements):
            last = (i == len(self.statements) - 1)
            result += stmt.tree_string(new_indent, last)
        return result


class BinaryExpression(ASTNode):
    """
    Binary operation: left operator right
    
    Examples: x + 5,  a * b,  x > 10,  x && y
    
    This node preserves operator precedence through the tree structure:
      x + y * z  becomes:
        BinaryOp(+)
        ├── Identifier(x)
        └── BinaryOp(*)
            ├── Identifier(y)
            └── Number(z)
    """
    
    def __init__(self, operator: str, left, right, line: int = 0):
        self.operator = operator
        self.left = left
        self.right = right
        self.line = line
    
    def to_dict(self) -> dict:
        return {
            "type": "BinaryExpression",
            "operator": self.operator,
            "left": self.left.to_dict(),
            "right": self.right.to_dict()
        }
    
    def tree_string(self, indent: str = "", is_last: bool = True) -> str:
        connector = "└── " if is_last else "├── "
        result = indent + connector + f"BinaryOp({self.operator})\n"
        new_indent = indent + ("    " if is_last else "│   ")
        result += self.left.tree_string(new_indent, False)
        result += self.right.tree_string(new_indent, True)
        return result


class UnaryExpression(ASTNode):
    """
    Unary operation: operator operand
    
    Examples: !flag,  -x
    """
    
    def __init__(self, operator: str, operand, line: int = 0):
        self.operator = operator
        self.operand = operand
        self.line = line
    
    def to_dict(self) -> dict:
        return {
            "type": "UnaryExpression",
            "operator": self.operator,
            "operand": self.operand.to_dict()
        }
    
    def tree_string(self, indent: str = "", is_last: bool = True) -> str:
        connector = "└── " if is_last else "├── "
        result = indent + connector + f"UnaryOp({self.operator})\n"
        new_indent = indent + ("    " if is_last else "│   ")
        result += self.operand.tree_string(new_indent, True)
        return result


class Literal(ASTNode):
    """
    A literal (constant) value: number, string, or boolean.
    
    Examples: 10, 3.14, "Hello", true, false
    """
    
    def __init__(self, value, literal_type: str = "NUMBER", line: int = 0):
        self.value = value
        self.literal_type = literal_type   # NUMBER, STRING, BOOLEAN
        self.line = line
    
    def to_dict(self) -> dict:
        return {
            "type": "Literal",
            "literal_type": self.literal_type,
            "value": self.value
        }
    
    def tree_string(self, indent: str = "", is_last: bool = True) -> str:
        connector = "└── " if is_last else "├── "
        if self.literal_type == "STRING":
            display = f'String("{self.value}")'
        elif self.literal_type == "BOOLEAN":
            display = f'Boolean({self.value})'
        else:
            display = f'Number({self.value})'
        return indent + connector + display + "\n"


class Identifier(ASTNode):
    """
    A variable reference (identifier).
    
    Example: x, price, myVar
    """
    
    def __init__(self, name: str, line: int = 0):
        self.name = name
        self.line = line
    
    def to_dict(self) -> dict:
        return {
            "type": "Identifier",
            "name": self.name
        }
    
    def tree_string(self, indent: str = "", is_last: bool = True) -> str:
        connector = "└── " if is_last else "├── "
        return indent + connector + f"Identifier({self.name})\n"
