# MiniLang Syntax Analyzer

A beginner-friendly **Compiler Front-End (Lexer + Recursive Descent Parser + AST Generator + Web Interface)** built for **Compiler Construction / Compiler Design** coursework.

---

## 🚀 How to Run

### Step 1: Open Terminal in the Project Directory
```bash
cd "c:\Users\Shreesh Pawar\OneDrive\Desktop\siddhant\minilang-syntax-analyzer"
```

### Step 2: Install Dependencies
```bash
pip install -r requirements.txt
```
*(Only Flask is required; the lexer and parser are implemented manually from scratch without external parser-generator libraries like Lex, Yacc, PLY, ANTLR, or Lark).*

### Step 3: Start the Flask Application
```bash
python app.py
```

### Step 4: Open in Your Browser
Open your browser and navigate to:
```text
http://127.0.0.1:5000
```

---

## 🧪 How to Run Tests

Run the manual test suites to verify tokenization and parsing:

```bash
# Run Lexer tests
python tests/test_lexer.py

# Run Parser tests
python tests/test_parser.py
```

---

## 🏗️ Compiler Architecture & Pipeline

```text
Source Code (MiniLang)
         ↓
  [ Lexical Analysis ]  (lexer/lexer.py)
         ↓
    Token Stream       (Token objects with line/column)
         ↓
  [ Syntax Analysis ]   (parser/parser.py - Recursive Descent)
         ↓
   ┌─────┴────────────────┐
   ↓                      ↓
  AST (Success)      Syntax Errors (Reported with Line & Col)
```

1. **Lexical Analysis (Lexer)**: Scans characters, strips whitespace & comments (`//`), and produces structured `Token` objects (`KEYWORD`, `ID`, `NUMBER`, `STRING`, `BOOLEAN`, operators, delimiters).
2. **Syntax Analysis (Parser)**: Recursive descent parser enforcing the Context-Free Grammar (CFG), checking token sequences and building an **Abstract Syntax Tree (AST)**.
3. **Error Reporting & Panic-Mode Recovery**: Pinpoints unexpected tokens with line number, column number, expected vs. actual tokens, and recovers at statement boundaries (`;`, `}`).

---

## 📜 MiniLang Context-Free Grammar (CFG)

```text
program          -> statement_list
statement_list   -> statement statement_list | ε

statement        -> declaration
                  | assignment
                  | if_statement
                  | while_statement
                  | print_statement
                  | block

declaration      -> ("int" | "float" | "bool") ID declaration_init ";"
declaration_init -> "=" expression | ε

assignment       -> ID "=" expression ";"

if_statement     -> "if" "(" expression ")" block else_part
else_part        -> "else" block | ε

while_statement  -> "while" "(" expression ")" block

print_statement  -> "print" "(" expression ")" ";"

block            -> "{" statement_list "}"

expression       -> logical_or
logical_or       -> logical_and ("||" logical_and)*
logical_and      -> equality ("&&" equality)*
equality         -> relational (("==" | "!=") relational)*
relational       -> additive (("<" | ">" | "<=" | ">=") additive)*
additive         -> term (("+" | "-") term)*
term             -> factor (("*" | "/" | "%") factor)*
factor           -> NUMBER | STRING | BOOLEAN | ID
                  | "(" expression ")"
                  | "!" factor
                  | "-" factor
```

---

## 📁 Project Structure

```text
minilang-syntax-analyzer/
├── app.py                 # Flask server & REST API (/analyze)
├── requirements.txt       # Dependencies (Flask)
├── README.md              # Complete educational & viva documentation
├── lexer/
│   ├── __init__.py
│   ├── tokens.py          # TokenType constants & Token class
│   └── lexer.py           # Character scanner & tokenizer
├── parser/
│   ├── __init__.py
│   ├── ast_nodes.py       # AST node representations
│   ├── errors.py          # SyntaxError data structure
│   └── parser.py          # Recursive descent parser
├── static/
│   ├── style.css          # Dark-mode compiler IDE styling
│   └── script.js          # API bridge, editor sync & AST viewer
├── templates/
│   └── index.html         # Web IDE interface
├── examples/
│   ├── valid_program.ml   # Valid test program
│   └── invalid_program.ml # Error handling test program
└── tests/
    ├── test_cases.py      # Test input suite
    ├── test_lexer.py      # Lexer unit tests
    └── test_parser.py     # Parser unit tests
```

## Phase 1 Enhancements

The project now includes a semantic-analysis phase after parsing:

- **Semantic Analyzer** for identifier and statement validation.
- **Scoped Symbol Table** with variable name, type, scope, declaration line, and initialization status.
- **Type Checking** for declarations, assignments, arithmetic, comparison, logical operators, unary operators, and conditions.
- **Nested Scope Support** allowing variables to be shadowed safely inside blocks.
- **Semantic Diagnostics** with line/column information and source-code caret highlighting.
- **Semantic Analysis UI** and **Symbol Table UI** in separate result tabs.
- **Automated semantic tests** covering valid programs, undeclared variables, duplicate declarations, type mismatches, boolean conditions, logical operators, and nested scopes.

### Updated Compiler Pipeline

`Source Code → Lexer → Tokens → Recursive Descent Parser → AST → Semantic Analyzer → Symbol Table + Type Checking`
