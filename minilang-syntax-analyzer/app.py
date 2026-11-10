"""MiniLang Compiler Construction web application."""

from flask import Flask, render_template, request, jsonify
from lexer import Lexer
from parser import Parser
from semantic import SemanticAnalyzer
from intermediate import ThreeAddressCodeGenerator
from statistics import CompilerStatistics

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/analyze", methods=["POST"])
def analyze():
    data = request.get_json()

    if not data or "code" not in data:
        return jsonify({
            "success": False,
            "tokens": [],
            "ast": None,
            "ast_tree": "",
            "semantic_errors": [],
            "symbol_table": [],
            "intermediate_code": [],
            "statistics": {},
            "errors": [{
                "message": "No source code provided",
                "line": 0,
                "column": 0,
                "kind": "Input Error",
            }],
        }), 400

    source_code = data["code"]

    if not source_code.strip():
        return jsonify({
            "success": True,
            "tokens": [],
            "ast": {"type": "Program", "statements": []},
            "ast_tree": "Program\n",
            "semantic_errors": [],
            "symbol_table": [],
            "intermediate_code": [],
            "statistics": {},
            "errors": [],
        })

    # Phase 1: lexical analysis
    lexer = Lexer(source_code)
    tokens, lexer_errors = lexer.tokenize()
    token_list = [t.to_dict() for t in tokens if t.type != "EOF"]
    all_errors = [e.to_dict() for e in lexer_errors]

    # Phase 1: syntax analysis / AST construction
    parser = Parser(tokens)
    ast_node, parser_errors = parser.parse()
    all_errors.extend([e.to_dict() for e in parser_errors])

    ast_dict = None
    ast_tree = ""
    if ast_node:
        ast_dict = ast_node.to_dict()
        ast_tree = ast_node.tree_string()

    # Phase 1: semantic analysis
    semantic_errors = []
    symbol_table = []
    if ast_node is not None and not lexer_errors and not parser_errors:
        analyzer = SemanticAnalyzer()
        semantic_error_objects, symbols = analyzer.analyze(ast_node)
        semantic_errors = [e.to_dict() for e in semantic_error_objects]
        symbol_table = [s.to_dict() for s in symbols]
        all_errors.extend(semantic_errors)

    # Phase 2: intermediate code + statistics are generated only for a
    # syntactically valid AST. This keeps broken programs from producing
    # misleading compiler output.
    intermediate_code = []
    if ast_node is not None and not lexer_errors and not parser_errors:
        generator = ThreeAddressCodeGenerator()
        intermediate_code = generator.generate(ast_node)

    stats = CompilerStatistics().calculate(
        program=ast_node,
        tokens=token_list,
        semantic_errors=semantic_errors,
        syntax_errors=all_errors[:len(lexer_errors) + len(parser_errors)],
    )

    success = len(all_errors) == 0

    return jsonify({
        "success": success,
        "tokens": token_list,
        "ast": ast_dict,
        "ast_tree": ast_tree,
        "semantic_errors": semantic_errors,
        "symbol_table": symbol_table,
        "intermediate_code": intermediate_code,
        "statistics": stats,
        "errors": all_errors,
    })


if __name__ == "__main__":
    print("=" * 55)
    print("  MiniLang Compiler Construction Project")
    print("  Lexical + Syntax + Semantic + Intermediate Analysis")
    print("=" * 55)
    print("  Server running at: http://127.0.0.1:5000")
    print("  Press Ctrl+C to stop")
    print("=" * 55)
    app.run(debug=True, port=5000)
