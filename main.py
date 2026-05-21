from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import sympy as sp
from sympy.parsing.sympy_parser import (
    parse_expr,
    standard_transformations,
    implicit_multiplication_application,
    convert_xor
)
import random

app = FastAPI()

x = sp.symbols('x')

from sympy.printing.str import StrPrinter

import re

superscripts = {
    "0": "⁰",
    "1": "¹",
    "2": "²",
    "3": "³",
    "4": "⁴",
    "5": "⁵",
    "6": "⁶",
    "7": "⁷",
    "8": "⁸",
    "9": "⁹",
    "-": "⁻"
}

def to_superscript(num: str):
    return "".join(superscripts.get(c, c) for c in num)

def format_expr(expr):
    s = str(expr)

    # Wurzeln
    s = s.replace("sqrt", "√")

    # Potenzen: x**2 → x²
    s = s.replace("**2", "<sup>2</sup>")
    s = s.replace("**3", "<sup>3</sup>")
    s = s.replace("**4", "<sup>4</sup>")

    # x**x → xˣ (Hochstellung)
    s = s.replace("**x", "<sup>x</sup>")

    # x*y → x·y
    s = s.replace("*", "·")

    return s
# 👉 Mathe-Eingabe clean machen
transformations = (
    standard_transformations +
    (implicit_multiplication_application, convert_xor)
)

categories = {

    # 🟢 Basics (11. Klasse)
    "polynomial": [
        x**2 + 3*x,
        2*x**3 - x,
        4*x**2 + 5*x,
        x**4 - x**2,
        6*x + 3,
        x**5 + 2*x**3,
        (x**2 + x),
        3*x**4 - x**2 + 2*x,
        x**6 + x,
        (2*x + 1)**2
    ],

    # 🟡 Kettenregel
    "chain": [
        (x**2 + 1)**3,
        (x**2 + x)**5,
        (3*x + 2)**4,
        (x**2 - 1)**2,
        (x + 5)**6,
        sp.sqrt(x**2 + 1),
        (x**2 + 4)**(3/2),
        (2*x**2 + 3*x + 1)**3,
        (x**3 + 1)**2,
    ],

    # 🔵 Produktregel (auch gemischt mit Wurzeln)
    "product": [
        (x**2 + 1)*(x**3 - x),
        x*(x**2 + 3)**4,
        x**2 * (x + 1)**2,
        (x + 2)*(x**2 + 1),
        x * sp.sqrt(x**2 + 1),
        (x**2 + 1) * sp.sqrt(x + 1),
        (x + 1)*(x**2 + 3)**2,
        x*(x**2 + 1)*(x + 2),
    ],

    # 🟣 Quotientenregel (auch mit trig / Wurzeln)
    "quotient": [
        (x**3 + 2*x)/(x**2 + 1),
        (x + 1)/(x**3 + 1),
        (x**2 + 1)/(x + 2),
        (x**3 - x)/(x + 1),
        (2*x + 3)/(x**2 + 4),
        sp.sin(x)/(x + 1),
        sp.cos(x)/(x**2 + 1),
        sp.sqrt(x)/(x + 1),
    ],

    # 🟠 Mixed (Trig + Exp + Produkt + Kette)
    "special": [
        x**2 * sp.sin(x),
        x * sp.cos(x),
        sp.exp(x) * x,
        sp.exp(x) * sp.sin(x),
        (x**2 + 1) * sp.cos(x),
        sp.sin(x) * sp.exp(x),
        x * sp.exp(x) * sp.cos(x),
    ],

    # 🔴 EXTREM (Abi+ – alles gemischt, aber sauber vereinfachbar)
    "extreme": [
        (x**2 + 1) * sp.sin(x),
        (x**2 + 1) * sp.cos(x),
        x * (x**2 + 1) * sp.sin(x),
        sp.exp(x) * (x**2 + 1) * sp.cos(x),
        (x**2 + 1)**2 * sp.sin(x),
        (x + 1) * sp.sqrt(x**2 + 1) * sp.cos(x),
        (x**2 + 1) / (x + 1) * sp.sin(x),
        x * sp.sqrt(x**2 + 1) * sp.exp(x),
        (x**2 + 1)**(3/2) * sp.cos(x),
        x * (x**2 + 1) * sp.exp(x),
    ]
}
current_category = "polynomial"


current_function = None
correct_answer = None


def new_task():
    global current_function, correct_answer

    current_function = random.choice(categories[current_category])

    correct_answer = sp.simplify(sp.diff(current_function, x))


new_task()


@app.get("/", response_class=HTMLResponse)
def home():
    return """
    <html>
    <head>
        <title>Mathe Trainer</title>
        <script src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"></script>

        <!-- 👉 schöne Mathe-/Schulschrift -->
        <link href="https://fonts.googleapis.com/css2?family=Computer+Modern+Serif&display=swap" rel="stylesheet">

        <style>
            body {
                font-family: 'Computer Modern Serif', serif;
                background-color: #f7f7fb;
                margin: 0;
                display: flex;
            }
           #sidebar {
                width: 220px;
                background: linear-gradient(180deg, #f7f9ff, #b8c6ff);
                height: 100vh;
                padding: 20px;
                box-sizing: border-box;
                text-align: left;
                backdrop-filter: blur(10px);
                box-shadow: 2px 0 10px rgba(0,0,0,0.1);
}

            #difficultyDisplay {
                font-size: 18px;
                margin-top: 10px;
                color: #555;
}
            #sidebar h2 {
                margin-top: 0;
}

            #sidebar button {
                width: 100%;
                margin-top: 10px;
}

            #main {
                flex: 1;
                text-align: center;
                padding: 40px;
}

            h1 {
                font-size: 40px;
            }

            #task {
                font-size: 28px;
                margin: 20px;
            }

            input {
                font-size: 18px;
                padding: 10px;
                width: 250px;
                border-radius: 8px;
                border: 1px solid #ccc;
            }

           #sidebar button {

    font-size: 18px;

    padding: 10px 15px;

    margin: 10px 0;

    border-radius: 8px;

    border: none;

    cursor: pointer;

    background-color: #4a6cf7;

    color: white;
}

#sidebar button:hover {

    background-color: #3557d6;
}

            #result {
                font-size: 22px;
                margin-top: 20px;
            }
            


.kb-wrap { background: #f0f0f5; border-radius: 12px; padding: 12px; max-width: 520px; margin: 20px auto; border: 1px solid #ddd; }
.kb-section { display: flex; gap: 10px; }
.kb-col { display: flex; flex-direction: column; gap: 5px; flex: 1; }
.kb-col-label { font-size: 11px; color: #888; text-align: center; margin-bottom: 3px; }
.kb-grid-2 { display: grid; grid-template-columns: 1fr 1fr; gap: 5px; }
.kb-grid-4 { display: grid; grid-template-columns: repeat(4, 1fr); gap: 5px; }
.kb-grid-3 { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 5px; }
.kb-btn { height: 48px; font-size: 16px; border: 1px solid #ccc; border-radius: 8px; background: white; color: #222; cursor: pointer; display: flex; flex-direction: column; align-items: center; justify-content: center; transition: background 0.1s; line-height: 1.2; }
.kb-btn small { font-size: 10px; color: #888; }
.kb-btn:hover { background: #e8eeff; color: #4a6cf7; border-color: #4a6cf7; }
.kb-btn.accent { background: #4a6cf7; color: white; border-color: #4a6cf7; }
.kb-btn.accent:hover { background: #3557d6; }
.kb-divider { width: 1px; background: #ddd; }
.action-buttons {

    margin-top: 20px;
}

.action-buttons button {

    font-size: 18px;

    padding: 12px 20px;

    margin: 10px;

    border-radius: 12px;

    border: none;

    background: #4a6cf7;

    color: white;

    cursor: pointer;

    transition: 0.15s;
}

.action-buttons button:hover {

    background: #3557d6;

    transform: translateY(-1px);
}

#preview {
    font-size: 28px;
    margin-top: 10px;
    min-height: 40px;
    color: #222;
}

        </style>
    </head>
    
    <body>
        <div id="sidebar">

    <h2>📘 Ableitungen</h2>

    <button onclick="setCategory('polynomial')">
    Polynome
    </button>

    <button onclick="setCategory('chain')">
    Kettenregel
    </button>

    <button onclick="setCategory('product')">
    Produktregel
    </button>

    <button onclick="setCategory('quotient')">
    Quotientenregel
    </button>

    <button onclick="setCategory('special')">
    Spezial
    </button>

    <button onclick="setCategory('extreme')">
    Extrem
    </button>

    </div>

    <div id="main">

        <h1>📘 Mathe Trainer</h1>
        

        <p>Leite ab:</p>
        <div id="task"></div>

        <div id="answer" contenteditable="true" spellcheck="false"
     placeholder="Tippe oder klicke Buttons..."
     style="font-size:20px; padding:10px; width:340px; border-radius:8px;
            border:1px solid #ccc; min-height:44px; display:inline-block;
            text-align:left; background:white; cursor:text;
            font-family:'Computer Modern Serif',serif; color:#222;"></div>

<style>
  #answer:empty:before { content: attr(placeholder); color: #aaa; }
</style>
        

        <br>
        
        

<div class="kb-wrap">
  <div class="kb-section">
    <div class="kb-col" style="max-width:195px;">
      <div class="kb-col-label">Funktionen</div>
      <div class="kb-grid-2">
        <div class="kb-btn" onclick="add('**')">xⁿ<small>Potenz</small></div>
        <div class="kb-btn" onclick="add('sqrt(')">√x<small>Wurzel</small></div>
        <div class="kb-btn" onclick="add('sin(')">sin</div>
        <div class="kb-btn" onclick="add('cos(')">cos</div>
        <div class="kb-btn" onclick="add('tan(')">tan</div>
        <div class="kb-btn" onclick="add('ln(')">ln</div>
        <div class="kb-btn" onclick="add('log(')">log</div>
        <div class="kb-btn" onclick="add('Abs(')">|x|</div>
        <div class="kb-btn" onclick="add('pi')">π</div>
        <div class="kb-btn" onclick="add('e')">𝑒</div>
      </div>
    </div>

    <div class="kb-divider"></div>

    <div class="kb-col">
      <div class="kb-col-label">Zahlen & Operatoren</div>
      <div class="kb-grid-4">
        <div class="kb-btn" onclick="add('7')">7</div>
        <div class="kb-btn" onclick="add('8')">8</div>
        <div class="kb-btn" onclick="add('9')">9</div>
        <div class="kb-btn" onclick="add('/')">÷</div>
        <div class="kb-btn" onclick="add('4')">4</div>
        <div class="kb-btn" onclick="add('5')">5</div>
        <div class="kb-btn" onclick="add('6')">6</div>
        <div class="kb-btn" onclick="add('*')">×</div>
        <div class="kb-btn" onclick="add('1')">1</div>
        <div class="kb-btn" onclick="add('2')">2</div>
        <div class="kb-btn" onclick="add('3')">3</div>
        <div class="kb-btn" onclick="add('-')">−</div>
        <div class="kb-btn" onclick="add('0')">0</div>
        <div class="kb-btn" onclick="add('.')">.</div>
        <div class="kb-btn" onclick="add('x')" style="font-style:italic">x</div>
        <div class="kb-btn" onclick="add('+')">+</div>
      </div>
      <div class="kb-grid-3" style="margin-top:5px;">
        <div class="kb-btn" onclick="add('(')">(</div>
        <div class="kb-btn" onclick="add(')')">)</div>
        <div class="kb-btn accent" onclick="clearInput()">⌫</div>
      </div>
    </div>
  </div>
</div>

        <div class="action-buttons">
    <button onclick="check()">Prüfen</button>
    <button onclick="nextTask()">Nächste Aufgabe</button>
</div>
        <div id="result"></div>

        <script>
        const display = document.getElementById("answer");

const PRETTY = {
    'sqrt(':  '√(',
    'pi':     'π',
    'e':      '𝑒',
    'x':      '𝑥',
    '**':     '^',
    '*':      '·',
    '/':      '÷',
    '-':      '−',
    'sin(':   'sin(',
    'cos(':   'cos(',
    'tan(':   'tan(',
    'ln(':    'ln(',
    'log(':   'log(',
    'Abs(':   '|',
};

function getRaw() {
    return display.textContent
        .replace(/√\(/g,   'sqrt(')
        .replace(/\^/g,    '**')
        .replace(/π/g,     'pi')
        .replace(/𝑒/g,     'e')
        .replace(/𝑥/g,     'x')
        .replace(/·/g,     '*')
        .replace(/÷/g,     '/')
        .replace(/−/g,     '-');
}

function insertAtCursor(text) {
    display.focus();
    const sel = window.getSelection();
    if (sel.rangeCount && display.contains(sel.getRangeAt(0).commonAncestorContainer)) {
        const range = sel.getRangeAt(0);
        range.deleteContents();
        const node = document.createTextNode(text);
        range.insertNode(node);
        range.setStartAfter(node);
        range.collapse(true);
        sel.removeAllRanges();
        sel.addRange(range);
    } else {
        // Cursor ans Ende setzen und dort einfügen
        const node = document.createTextNode(text);
        display.appendChild(node);
        const range = document.createRange();
        const sel2 = window.getSelection();
        range.setStartAfter(node);
        range.collapse(true);
        sel2.removeAllRanges();
        sel2.addRange(range);
    }
}

function clearInput() {
    display.textContent = "";
    document.getElementById("preview").innerHTML = "";
    display.focus();
}

// Auto-ersetze beim manuellen Tippen (z.B. "sqrt(" → "√(")
const REPLACEMENTS = [
    [/sqrt\(/g, '√('],
    [/\*\*/g,   '^'],
    [/\bpi\b/g, 'π'],
    [/\be\b/g,  '𝑒'],
    [/\bx\b/g,  '𝑥'],
    [/\*/g,     '·'],
    [/\//g,     '÷'],
];

display.addEventListener("input", function () {
    let text = display.textContent;
    let replaced = text;
    for (const [from, to] of REPLACEMENTS) replaced = replaced.replace(from, to);
    if (replaced !== text) {
        // Cursor ans Ende setzen nach Ersetzung
        display.textContent = replaced;
        const range = document.createRange();
        const sel = window.getSelection();
        range.selectNodeContents(display);
        range.collapse(false);
        sel.removeAllRanges();
        sel.addRange(range);
    }
    updatePreview();
});

async function updatePreview() {
    const raw = getRaw().trim();
    const preview = document.getElementById("preview");
    if (!raw) { preview.innerHTML = ""; return; }
    try {
        const res = await fetch("/preview?expr=" + encodeURIComponent(raw));
        const data = await res.json();
        if (data.latex) {
            preview.innerHTML = "\\(" + data.latex + "\\)";
            MathJax.typesetPromise([preview]);
        }
    } catch(e) {}
}

async function loadTask() {
    const res = await fetch("/task");
    const data = await res.json();
    document.getElementById("task").innerHTML = "$$" + data.task + "$$";
    MathJax.typesetPromise();
}

async function check() {
    const ans = getRaw();
    const res = await fetch("/check?answer=" + encodeURIComponent(ans));
    const data = await res.json();
    document.getElementById("result").innerHTML = data.feedback;
    MathJax.typesetPromise();
}

async function nextTask() {
    await fetch("/next");
    display.textContent = "";
    document.getElementById("result").innerHTML = "";
    document.getElementById("preview").innerHTML = "";
    await loadTask();
}

async function setCategory(cat) {
    await fetch("/category?name=" + cat);
    display.textContent = "";
    document.getElementById("result").innerHTML = "";
    document.getElementById("preview").innerHTML = "";
    await loadTask();
}

loadTask();
    </script>
    </div> <!-- closes main -->
    </body>
    </html>
    """


@app.get("/task")
def task():
    import sympy as sp
    return {"task": sp.latex(current_function, symbol_names={sp.pi: r"\pi"})}
@app.get("/preview")
def preview(expr: str):
    try:
        parsed = parse_expr(
            expr.strip(),
            transformations=transformations,
            local_dict={
                "x": x, "sin": sp.sin, "cos": sp.cos, "tan": sp.tan,
                "exp": sp.exp, "sqrt": sp.sqrt, "log": sp.log,
                "ln": sp.log, "pi": sp.pi, "E": sp.E, "e": sp.E, "Abs": sp.Abs,
            }
        )
        return {"latex": sp.latex(parsed)}
    except Exception:
        return {"latex": ""}


@app.get("/next")
def next_task():
    new_task()
    return {"ok": True}
@app.get("/category")
def set_category(name: str):

    global current_category

    if name in categories:
        current_category = name
    else:
        return {"ok": False}
    new_task()

    return {"ok": True}

def same_math(a, b):
    d = a - b
    tests = [
        d,
        sp.simplify(d),
        sp.together(d),
        sp.cancel(d),
        sp.trigsimp(d),
    ]
    for t in tests:
        try:
            if t is not None and t.equals(0) is True:
                return True
        except Exception:
            pass
    return False



    base = sp.simplify(expr)

    forms = [
        base,
        sp.expand(base),
        sp.factor(base),
        sp.trigsimp(base),
        sp.cancel(sp.together(base)),
        sp.together(base),
        sp.powsimp(base, force=True),
    ]

    unique = []
    seen = set()

    for f in forms:
        try:
            key = sp.srepr(f)
        except Exception:
            key = str(f)

        if key not in seen:
            seen.add(key)
            unique.append(f)

    return unique


@app.get("/check")
def check(answer: str):
    try:
        raw = answer.strip()

        if not raw:
            return {
                "correct": False,
                "feedback": "⚠ Schreib z.B. 2x+3"
            }

        low = raw.lower()
        if "diff" in low or "derivative" in low:
            return {
                "correct": False,
                "feedback": "⚠ Bitte leite selbst ab, nicht mit diff()"
            }

        user = parse_expr(
            raw,
            transformations=transformations,
            local_dict={
                "x": x,
                "sin": sp.sin,
                "cos": sp.cos,
                "tan": sp.tan,
                "exp": sp.exp,
                "sqrt": sp.sqrt,
                "log": sp.log,
                "ln": sp.log,
                "pi": sp.pi,
                "E": sp.E,
                "e": sp.E,
                "Abs": sp.Abs,
            }
        )

        correct = sp.simplify(correct_answer)
        user_s = sp.simplify(user)

        # 1) mathematisch falsch
        if not same_math(user_s, correct):
            return {
                "correct": False,
                "feedback": "❌ Falsch. Lösung: \\(" + sp.latex(correct) + "\\)"
            }

        # 2) mathematisch richtig, aber noch nicht in einer einfachen Form
        preferred = sp.simplify(correct)

        if sp.simplify(user_s - preferred) != 0:
            return {
                "correct": False,
                "feedback": "⚠ Richtig, aber bitte weiter vereinfachen!"
            }

        # 3) gut genug
        return {"correct": True, "feedback": "✅ Richtig!"}

    except Exception:
        return {
            "correct": False,
            "feedback": "⚠ Schreib z.B. 2x+3"
        }