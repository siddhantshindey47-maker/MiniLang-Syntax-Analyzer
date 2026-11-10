"""
test_cases.py — Test Input Data for MiniLang
=============================================

This file contains all the valid and invalid test cases
used by test_lexer.py and test_parser.py.
"""

# ─── Valid Programs ───────────────────────────────────────

VALID_CASES = {
    "simple_declaration": "int x;",
    
    "declaration_with_init": "int x = 10;",
    
    "float_declaration": "float price = 25.5;",
    
    "bool_declaration": "bool flag = true;",
    
    "assignment": "int x = 10;\nx = x + 5;",
    
    "arithmetic_precedence": "int x = 10 + 20 * 2;",
    
    "parentheses": "int x = (10 + 20) * 2;",
    
    "if_statement": """int x = 10;
if (x > 5) {
    print(x);
}""",
    
    "if_else": """int x = 10;
if (x > 5) {
    print("greater");
} else {
    print("not greater");
}""",
    
    "while_loop": """int x = 0;
while (x < 10) {
    x = x + 1;
}""",
    
    "print_string": 'print("Hello World");',
    
    "print_expression": "int x = 42;\nprint(x);",
    
    "logical_operators": "bool result = true && false || !true;",
    
    "relational_operators": """int x = 10;
int y = 20;
bool r1 = x < y;
bool r2 = x >= y;
bool r3 = x == y;
bool r4 = x != y;""",
    
    "block": """{
    int x = 10;
    print(x);
}""",
    
    "nested_if": """int x = 15;
if (x > 10) {
    if (x > 20) {
        print("very large");
    } else {
        print("medium");
    }
}""",
    
    "complex_expression": "int result = (10 + 20) * (30 - 5) / 2 % 7;",
    
    "unary_minus": "int x = -10;",
    
    "unary_not": "bool flag = !true;",
    
    "comments": """// This is a comment
int x = 10; // Inline comment
// Another comment
print(x);""",
    
    "empty_program": "",
    
    "complex_program": """int x = 10;
int y = 20;
float pi = 3.14;
bool isValid = true;

int result = x + y * 2 - 5;
print(result);

if (x < y && isValid) {
    int temp = x;
    x = y;
    y = temp;
} else {
    print("no swap");
}

int i = 0;
while (i < 10) {
    if (i % 2 == 0) {
        print(i);
    }
    i = i + 1;
}

print("Done!");"""
}


# ─── Invalid Programs ────────────────────────────────────

INVALID_CASES = {
    "missing_semicolon": {
        "code": "int x = 10",
        "description": "Missing semicolon after declaration"
    },
    
    "missing_expression": {
        "code": "int x = 10;\nx = 10 + ;",
        "description": "Missing expression after operator"
    },
    
    "missing_close_paren": {
        "code": "int x = 10;\nif (x > 10 {\n    print(x);\n}",
        "description": "Missing closing parenthesis in if condition"
    },
    
    "missing_close_brace": {
        "code": "int x = 10;\nif (x > 10) {\n    print(x);",
        "description": "Missing closing brace"
    },
    
    "invalid_declaration_type": {
        "code": "integer x;",
        "description": "Invalid type keyword ('integer' instead of 'int')"
    },
    
    "empty_assignment": {
        "code": "int x = 10;\nx = ;",
        "description": "Missing value in assignment"
    },
    
    "missing_condition_paren": {
        "code": "int x = 10;\nwhile x < 10 {\n    x = x + 1;\n}",
        "description": "Missing parentheses around while condition"
    },
    
    "missing_print_paren": {
        "code": "print x;",
        "description": "Missing parentheses in print statement"
    }
}
