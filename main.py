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
            

.math-grid {
    display: grid;
    grid-template-columns: repeat(5, 72px);
    gap: 10px;

    justify-content: center;

    margin: 25px auto;

    max-width: 420px;
}

.math-grid button {

    height: 60px;

    font-size: 22px;

    border: 1px solid #bbb;

    border-radius: 14px;

    background: white;

    color: #222;

    cursor: pointer;

    transition: 0.15s;
}

.math-grid button:hover {

    background: #f2f2f2;

    transform: translateY(-1px);
}
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

        <input id="answer" placeholder="Tippe oder klicke Buttons..." style="width: 340px;">
        <div id="preview"></div>

        <br>
        
        

<div class="math-grid">

<button onclick="add('7')">7</button>
<button onclick="add('8')">8</button>
<button onclick="add('9')">9</button>
<button onclick="add('+')">+</button>
<button onclick="add('-')">−</button>

<button onclick="add('4')">4</button>
<button onclick="add('5')">5</button>
<button onclick="add('6')">6</button>
<button onclick="add('*')">·</button>
<button onclick="add('/')">/</button>

<button onclick="add('1')">1</button>
<button onclick="add('2')">2</button>
<button onclick="add('3')">3</button>
<button onclick="add('(')">(</button>
<button onclick="add(')')">)</button>

<button onclick="add('0')">0</button>
<button onclick="add('.')">.</button>
<button onclick="add('x')">𝑥</button>
<button onclick="add('^')">^</button>
<button onclick="add('sqrt(')">√</button>
<button onclick="add('pi')">π</button>

<button onclick="add('sin(')">sin</button>
<button onclick="add('cos(')">cos</button>
<button onclick="add('tan(')">tan</button>
<button onclick="add('ln(')">ln</button>
<button onclick="add('log(')">log</button>
<button onclick="add('e')">𝑒</button>
<button onclick="clearInput()">⌫</button>

</div>

        <div class="action-buttons">
    <button onclick="check()">Prüfen</button>
    <button onclick="nextTask()">Nächste Aufgabe</button>
</div>
        <div id="result"></div>

        <script>
        
        let answered = false;

async function loadTask() {
    const res = await fetch("/task");
    const data = await res.json();
    document.getElementById("task").innerHTML = "$$" + data.task + "$$";
    
    MathJax.typesetPromise();
}

async function check() {
    const ans = document.getElementById("answer").value;
    const res = await fetch("/check?answer=" + encodeURIComponent(ans));
    const data = await res.json();
    document.getElementById("result").innerHTML = data.feedback;
    
    MathJax.typesetPromise();
}

async function nextTask() {
    await fetch("/next");
    document.getElementById("answer").value = "";
    document.getElementById("result").innerHTML = "";
    answered = false;
    await loadTask();
}

async function setCategory(cat) {
    await fetch("/category?name=" + cat);
    document.getElementById("answer").value = "";
    document.getElementById("result").innerHTML = "";
    answered = false;
    await loadTask();
}

function add(val) {
    const input = document.getElementById("answer");
    if (val === "^") val = "**";
    input.value += val;



input.focus();
}

function clearInput() {
    const input = document.getElementById("answer");
    input.value = "";
    document.getElementById("preview").innerHTML = "";
    input.focus();
}

loadTask();

document.getElementById("answer").addEventListener("input", function () {
    const val = this.value;
    document.getElementById("preview").innerHTML = toPretty(val);
});
    

function toPretty(val) {
    return val
        .replace(/\bpi\b/g, "π")
        .replace(/\bsqrt\(/g, "√(")
        .replace(/\bln\(/g, "ln(")
        .replace(/\blog\(/g, "log(")
        .replace(/\be\b/g, "𝑒")
        .replace(/\bx\b/g, "𝑥")
        .replace(/\*\*2/g, "²")
        .replace(/\*\*3/g, "³")
        .replace(/\*\*4/g, "⁴")
        .replace(/\*/g, "·");
}
    </script>
    </div> <!-- closes main -->
    </body>
    </html>
    """


@app.get("/task")
def task():
    import sympy as sp
    return {"task": sp.latex(current_function)}


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