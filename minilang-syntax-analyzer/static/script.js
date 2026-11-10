/**
 * script.js — MiniLang Syntax Analyzer Frontend
 * ==============================================
 * 
 * Handles:
 *  - Sending source code to the Flask /analyze API
 *  - Displaying tokens, AST, and errors
 *  - Loading example programs
 *  - Line number updates and cursor tracking
 */

// ═══════════════════════════════════════════════════════════
//  EXAMPLE PROGRAMS
// ═══════════════════════════════════════════════════════════

const EXAMPLES = {
    hello: `// Hello World in MiniLang
print("Hello, World!");`,

    variables: `// Variable Declarations
int x = 10;
float price = 25.5;
bool flag = true;

// Print the values
print(x);
print(price);`,

    arithmetic: `// Arithmetic Expressions
int a = 10;
int b = 20;
int sum = a + b;
int product = a * b;
int result = (a + b) * 2 - 5;

print(sum);
print(product);
print(result);`,

    ifelse: `// If-Else Statement
int x = 15;
int y = 10;

if (x > y) {
    print("x is greater");
    int diff = x - y;
    print(diff);
} else {
    print("y is greater or equal");
}`,

    while: `// While Loop
int count = 0;

while (count < 5) {
    print(count);
    count = count + 1;
}

print("Loop finished!");`,

    complex: `// Complex MiniLang Program
// Demonstrates all language features

int x = 10;
int y = 20;
float pi = 3.14;
bool isValid = true;

// Arithmetic with precedence
int result = x + y * 2 - 5;
print(result);

// Nested if-else
if (x < y && isValid) {
    print("Condition met!");
    
    int temp = x;
    x = y;
    y = temp;
    
    if (x > 15) {
        print("x is now large");
    } else {
        print("x is still small");
    }
} else {
    print("Condition not met");
}

// While loop with complex condition
int i = 0;
while (i < 10) {
    if (i % 2 == 0) {
        print(i);
    }
    i = i + 1;
}

// Logical expressions
bool check = x > 5 && y < 30 || !isValid;
print("Done!");`,

    error_semicolon: `// Error: Missing semicolon
int x = 10
int y = 20;`,

    error_paren: `// Error: Missing closing parenthesis
int x = 10;
if (x > 5 {
    print(x);
}`,

    error_brace: `// Error: Missing closing brace
int x = 10;
if (x > 5) {
    print(x);
`,

    error_expression: `// Error: Invalid expression
int x = 10;
x = 10 + ;
int y = ;`
};


// ═══════════════════════════════════════════════════════════
//  DOM REFERENCES
// ═══════════════════════════════════════════════════════════

const editor        = document.getElementById('code-editor');
const lineNumbers   = document.getElementById('line-numbers');
const lineInfo      = document.getElementById('line-info');
const statusBanner  = document.getElementById('status-banner');
const statusIcon    = document.getElementById('status-icon');
const statusText    = document.getElementById('status-text');
const resultTabs    = document.getElementById('result-tabs');
const tokenBody     = document.getElementById('token-body');
const tokenCount    = document.getElementById('token-count');
const astDisplay    = document.getElementById('ast-display');
const astVisual     = document.getElementById('ast-visual');
const tacList       = document.getElementById('tac-list');
const tacCount      = document.getElementById('tac-count');
const statsGrid     = document.getElementById('stats-grid');
const errorList     = document.getElementById('error-list');
const errorCount    = document.getElementById('error-count');
const semanticList  = document.getElementById('semantic-list');
const semanticCount = document.getElementById('semantic-count');
const semanticSummary = document.getElementById('semantic-summary');
const symbolBody    = document.getElementById('symbol-body');
const symbolCount   = document.getElementById('symbol-count');
const placeholder   = document.getElementById('placeholder');
const btnAnalyze    = document.getElementById('btn-analyze');


// ═══════════════════════════════════════════════════════════
//  LINE NUMBER TRACKING
// ═══════════════════════════════════════════════════════════

function updateLineNumbers() {
    const lines = editor.value.split('\n');
    const count = lines.length;
    let nums = '';
    for (let i = 1; i <= count; i++) {
        nums += i + '\n';
    }
    lineNumbers.textContent = nums;
}

function updateCursorInfo() {
    const text = editor.value.substring(0, editor.selectionStart);
    const lines = text.split('\n');
    const line = lines.length;
    const col = lines[lines.length - 1].length + 1;
    lineInfo.textContent = `Line ${line}, Col ${col}`;
}

// Sync line numbers and cursor info on input
editor.addEventListener('input', () => {
    updateLineNumbers();
    updateCursorInfo();
});

editor.addEventListener('click', updateCursorInfo);
editor.addEventListener('keyup', updateCursorInfo);

// Sync scroll between editor and line numbers
editor.addEventListener('scroll', () => {
    lineNumbers.scrollTop = editor.scrollTop;
});

// Handle Tab key in editor (insert spaces instead of changing focus)
editor.addEventListener('keydown', (e) => {
    if (e.key === 'Tab') {
        e.preventDefault();
        const start = editor.selectionStart;
        const end = editor.selectionEnd;
        editor.value = editor.value.substring(0, start) + '    ' + editor.value.substring(end);
        editor.selectionStart = editor.selectionEnd = start + 4;
        updateLineNumbers();
    }
});

// Initialize line numbers
updateLineNumbers();


// ═══════════════════════════════════════════════════════════
//  ANALYZE CODE
// ═══════════════════════════════════════════════════════════

async function analyzeCode() {
    const code = editor.value;
    
    if (!code.trim()) {
        showStatus('error', '!', 'Please type or paste some MiniLang code first.');
        return;
    }

    // Show loading state
    btnAnalyze.classList.add('loading');
    btnAnalyze.textContent = 'Analyzing…';

    // Animate pipeline
    animatePipeline();

    try {
        const response = await fetch('/analyze', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ code })
        });

        const data = await response.json();
        displayResults(data);

    } catch (err) {
        showStatus('error', '✕', 'Could not reach the server. Make sure the Flask app is still running, then try again.');
        console.error('Analyze error:', err);
    } finally {
        btnAnalyze.classList.remove('loading');
        btnAnalyze.textContent = 'Analyze';
    }
}


// ═══════════════════════════════════════════════════════════
//  DISPLAY RESULTS
// ═══════════════════════════════════════════════════════════

function displayResults(data) {
    // Hide placeholder, show tabs
    placeholder.style.display = 'none';
    resultTabs.style.display = 'flex';
    statusBanner.style.display = 'flex';

    // ─── Status ───
    if (data.success) {
        showStatus('success', '✓', 'Looks good — no errors found in your program.');
    } else {
        const count = data.errors.length;
        const semanticCountValue = data.semantic_errors ? data.semantic_errors.length : 0;
        const label = semanticCountValue > 0 ? 'Found problems in your program' : 'Found syntax errors';
        showStatus('error', '✕', `${label} — <span class="count">${count}</span> issue${count > 1 ? 's' : ''} to fix. See the Errors tab for details.`);
    }

    // ─── Tokens ───
    displayTokens(data.tokens);

    // ─── AST ───
    if (data.ast_tree) {
        astDisplay.textContent = data.ast_tree;
        astDisplay.dataset.tree = data.ast_tree;
    } else if (data.ast) {
        astDisplay.textContent = JSON.stringify(data.ast, null, 2);
        astDisplay.dataset.tree = astDisplay.textContent;
    } else {
        astDisplay.textContent = 'The syntax tree could not be built because of syntax errors.';
        astDisplay.dataset.tree = '';
    }
    renderAST(data.ast);

    // ─── Semantic Analysis ───
    displaySemanticResults(data.semantic_errors || []);

    // ─── Symbol Table ───
    displaySymbolTable(data.symbol_table || []);

    // ─── Phase 2: Intermediate Code ───
    displayThreeAddressCode(data.intermediate_code || []);

    // ─── Phase 2: Statistics ───
    displayStatistics(data.statistics || {});

    // ─── Errors ───
    displayErrors(data.errors, codeFromEditor());

    // Auto-switch to errors tab if there are errors
    if (!data.success && data.errors.length > 0) {
        switchTab('errors');
    } else {
        switchTab('tokens');
    }
}

function displayTokens(tokens) {
    tokenBody.innerHTML = '';
    tokenCount.textContent = `${tokens.length} token${tokens.length === 1 ? '' : 's'}`;

    tokens.forEach((t, i) => {
        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td>${i + 1}</td>
            <td><span class="token-type">${escapeHtml(t.type)}</span></td>
            <td><span class="token-value">${escapeHtml(t.value)}</span></td>
            <td>${t.line}</td>
            <td>${t.column}</td>
        `;
        tr.style.animationDelay = `${i * 15}ms`;
        tokenBody.appendChild(tr);
    });
}

function codeFromEditor() { return editor.value; }

function displaySemanticResults(errors) {
    semanticCount.textContent = `${errors.length} error${errors.length === 1 ? '' : 's'}`;
    semanticSummary.innerHTML = errors.length === 0
        ? '<div class="semantic-ok">All good. Variables are declared before use and the types match everywhere.</div>'
        : '<div class="semantic-bad">Some variables or types don\'t line up. The exact locations are listed below and in the Errors tab.</div>';
    semanticList.innerHTML = '';
    errors.forEach((err, i) => {
        const div = document.createElement('div');
        div.className = 'error-item semantic-error';
        div.style.animationDelay = `${i * 80}ms`;
        div.innerHTML = `<div class="error-location">${escapeHtml(err.kind || 'Semantic Error')} — Line ${err.line}, Column ${err.column}</div><div class="error-message">${escapeHtml(err.message)}</div>`;
        semanticList.appendChild(div);
    });
}

function displaySymbolTable(symbols) {
    symbolCount.textContent = `${symbols.length} symbol${symbols.length === 1 ? '' : 's'}`;
    symbolBody.innerHTML = '';
    symbols.forEach((symbol, i) => {
        const tr = document.createElement('tr');
        tr.innerHTML = `<td>${i + 1}</td><td><strong>${escapeHtml(symbol.name)}</strong></td><td><span class="token-type">${escapeHtml(symbol.type)}</span></td><td>${escapeHtml(symbol.scope)}</td><td>${symbol.line}</td><td>${symbol.initialized ? 'Has a value' : 'Declared only'}</td>`;
        symbolBody.appendChild(tr);
    });
    if (!symbols.length) {
        symbolBody.innerHTML = '<tr><td colspan="6" style="text-align:center;padding:30px;">No variables declared yet.</td></tr>';
    }
}

function displayThreeAddressCode(instructions) {
    tacCount.textContent = `${instructions.length} instruction${instructions.length === 1 ? '' : 's'}`;
    tacList.innerHTML = '';

    if (!instructions.length) {
        tacList.innerHTML = '<div class="placeholder"><h3>No intermediate code</h3><p>This is generated once your program has no syntax errors.</p></div>';
        return;
    }

    instructions.forEach((item, index) => {
        const row = document.createElement('div');
        row.className = `tac-row tac-${escapeHtml(item.kind || 'instruction')}`;
        row.innerHTML = `<span class="tac-number">${index + 1}</span><code>${escapeHtml(item.code)}</code><span class="tac-kind">${escapeHtml(item.kind || 'instruction')}</span>`;
        tacList.appendChild(row);
    });
}

function displayStatistics(stats) {
    statsGrid.innerHTML = '';
    const cards = [
        ['tokens', '', 'Tokens'],
        ['ast_nodes', '', 'Syntax tree nodes'],
        ['declarations', '', 'Declarations'],
        ['assignments', '', 'Assignments'],
        ['expressions', '', 'Expressions'],
        ['identifiers', '', 'Identifiers'],
        ['literals', '', 'Literals'],
        ['if_statements', '', 'If statements'],
        ['while_statements', '', 'While loops'],
        ['print_statements', '', 'Print statements'],
        ['blocks', '', 'Blocks'],
        ['semantic_errors', '', 'Semantic errors'],
        ['syntax_errors', '', 'Syntax errors'],
    ];

    if (!Object.keys(stats).length) {
        statsGrid.innerHTML = '<div class="placeholder"><h3>No statistics yet</h3><p>Analyze a program to see how many declarations, loops, and more it contains.</p></div>';
        return;
    }

    cards.forEach(([key, icon, label]) => {
        const card = document.createElement('div');
        card.className = 'stat-card';
        card.innerHTML = `<div class="stat-value">${stats[key] ?? 0}</div><div class="stat-label">${label}</div>`;
        statsGrid.appendChild(card);
    });
}

function renderAST(ast) {
    astVisual.innerHTML = '';
    if (!ast) {
        astVisual.innerHTML = '<div class="placeholder"><h3>No syntax tree</h3><p>Fix the syntax errors listed in the Errors tab, then analyze again.</p></div>';
        return;
    }

    const root = buildASTNode(ast);
    astVisual.appendChild(root);
}

function buildASTNode(node) {
    const wrapper = document.createElement('div');
    wrapper.className = 'ast-node-wrapper';

    const card = document.createElement('button');
    card.type = 'button';
    card.className = 'ast-node-card';
    card.innerHTML = `<strong>${escapeHtml(formatASTTitle(node))}</strong><span>${escapeHtml(formatASTMeta(node))}</span>`;
    card.title = 'Click to see details for this node';
    card.addEventListener('click', () => {
        document.querySelectorAll('.ast-node-card.selected').forEach(n => n.classList.remove('selected'));
        card.classList.add('selected');
        showASTDetails(node);
    });
    wrapper.appendChild(card);

    const children = getASTChildren(node);
    if (children.length) {
        const childContainer = document.createElement('div');
        childContainer.className = 'ast-children';
        children.forEach(child => childContainer.appendChild(buildASTNode(child)));
        wrapper.appendChild(childContainer);
    }
    return wrapper;
}

function formatASTTitle(node) {
    if (!node || !node.type) return 'Unknown';
    if (node.type === 'Declaration') return `Declaration: ${node.var_type} ${node.name}`;
    if (node.type === 'Assignment') return `Assignment: ${node.name}`;
    if (node.type === 'BinaryExpression') return `Binary: ${node.operator}`;
    if (node.type === 'UnaryExpression') return `Unary: ${node.operator}`;
    if (node.type === 'Identifier') return `Identifier: ${node.name}`;
    if (node.type === 'Literal') return `Literal: ${node.value}`;
    return node.type;
}

function formatASTMeta(node) {
    if (node.type === 'Literal') return node.literal_type || 'literal';
    if (node.type === 'Declaration') return node.var_type;
    if (node.type === 'BinaryExpression' || node.type === 'UnaryExpression') return `operator ${node.operator}`;
    return 'AST node';
}

function getASTChildren(node) {
    if (!node) return [];
    const children = [];
    if (Array.isArray(node.statements)) children.push(...node.statements);
    if (node.value && typeof node.value === 'object') children.push(node.value);
    if (node.condition) children.push(node.condition);
    if (node.then) children.push(node.then);
    if (node.else) children.push(node.else);
    if (node.body) children.push(node.body);
    if (node.argument) children.push(node.argument);
    if (node.left) children.push(node.left);
    if (node.right) children.push(node.right);
    if (node.operand) children.push(node.operand);
    return children;
}

function showASTDetails(node) {
    const details = `Type: ${node.type}\n${Object.entries(node).filter(([k]) => !['statements','value','condition','then','else','body','argument','left','right','operand'].includes(k)).map(([k,v]) => `${k}: ${v}`).join('\n')}`;
    astDisplay.textContent = details + '\n\n' + (astDisplay.dataset.tree || '');
}

function displayErrors(errors, source) {
    errorList.innerHTML = '';

    if (errors.length === 0) {
        errorList.innerHTML = '<div style="text-align:center;padding:40px;color:var(--text-secondary);">No errors found.</div>';
        errorCount.style.display = 'none';
    } else {
        errorCount.textContent = errors.length;
        errorCount.style.display = 'inline-flex';

        errors.forEach((err, i) => {
            const div = document.createElement('div');
            div.className = 'error-item';
            div.style.animationDelay = `${i * 80}ms`;
            const lines = source.split('\n');
            const sourceLine = err.line > 0 && err.line <= lines.length ? lines[err.line - 1] : '';
            const caretSpaces = ' '.repeat(Math.max(0, (err.column || 1) - 1));
            div.innerHTML = `
                <div class="error-location">${escapeHtml(err.kind || 'Syntax Error')} — Line ${err.line}, Column ${err.column}</div>
                <div class="error-message">${escapeHtml(err.message)}</div>
                ${sourceLine ? `<pre class="error-code">${escapeHtml(sourceLine)}\n<span class="error-caret">${caretSpaces}^</span></pre>` : ''}
            `;
            div.addEventListener('click', () => focusEditorLine(err.line, err.column));
            errorList.appendChild(div);
        });
    }
}


// ═══════════════════════════════════════════════════════════
//  UI HELPERS
// ═══════════════════════════════════════════════════════════

function focusEditorLine(line, column = 1) {
    if (!line || line < 1) return;
    const lines = editor.value.split('\n');
    let position = 0;
    for (let i = 0; i < line - 1 && i < lines.length; i++) position += lines[i].length + 1;
    position += Math.max(0, column - 1);
    editor.focus();
    editor.selectionStart = editor.selectionEnd = Math.min(position, editor.value.length);
    const lineHeight = parseFloat(getComputedStyle(editor).lineHeight) || 24;
    editor.scrollTop = Math.max(0, (line - 1) * lineHeight - editor.clientHeight / 3);
    updateCursorInfo();
}

function showStatus(type, icon, text) {
    statusBanner.style.display = 'flex';
    statusBanner.className = `status-banner ${type}`;
    statusIcon.textContent = icon;
    statusText.innerHTML = text;
}

function switchTab(tabName) {
    // Update tab buttons
    document.querySelectorAll('.tab').forEach(tab => {
        tab.classList.toggle('active', tab.dataset.tab === tabName);
    });

    // Update tab content
    document.querySelectorAll('.tab-content').forEach(content => {
        content.classList.toggle('active', content.id === `tab-${tabName}`);
    });
}

function animatePipeline() {
    const steps = document.querySelectorAll('.pipeline-step');
    steps.forEach((step, i) => {
        step.classList.remove('active');
        setTimeout(() => {
            step.classList.add('active');
            // Remove active class after animation except for the last step
            if (i < steps.length - 1) {
                setTimeout(() => step.classList.remove('active'), 600);
            }
        }, i * 200);
    });
}

function clearEditor() {
    editor.value = '';
    updateLineNumbers();
    
    // Reset results
    placeholder.style.display = 'flex';
    resultTabs.style.display = 'none';
    statusBanner.style.display = 'none';
    tokenBody.innerHTML = '';
    astDisplay.textContent = '';
    astDisplay.dataset.tree = '';
    astVisual.innerHTML = '';
    tacList.innerHTML = '';
    tacCount.textContent = '';
    statsGrid.innerHTML = '';
    errorList.innerHTML = '';
    errorCount.style.display = 'none';
    tokenCount.textContent = '';
    semanticCount.textContent = '';
    semanticSummary.innerHTML = '';
    semanticList.innerHTML = '';
    symbolBody.innerHTML = '';
    symbolCount.textContent = '';

    // Clear pipeline
    document.querySelectorAll('.pipeline-step').forEach(s => s.classList.remove('active'));

    editor.focus();
}

function toggleExamples() {
    const dropdown = document.getElementById('example-dropdown');
    dropdown.classList.toggle('open');
}

function loadExample(name) {
    if (EXAMPLES[name]) {
        editor.value = EXAMPLES[name];
        updateLineNumbers();
    }
    // Close dropdown
    document.getElementById('example-dropdown').classList.remove('open');
    editor.focus();
}

// Close dropdown when clicking outside
document.addEventListener('click', (e) => {
    const dropdown = document.getElementById('example-dropdown');
    if (!dropdown.contains(e.target)) {
        dropdown.classList.remove('open');
    }
});

// Keyboard shortcut: Ctrl+Enter to analyze
document.addEventListener('keydown', (e) => {
    if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
        e.preventDefault();
        analyzeCode();
    }
});

// Utility: escape HTML to prevent XSS
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}
