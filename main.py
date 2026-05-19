from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from sympy import symbols, diff, simplify
from sympy.parsing.sympy_parser import (
    parse_expr,
    standard_transformations,
    implicit_multiplication_application,
    convert_xor
)
import random

app = FastAPI()

x = symbols('x')

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

    # 1) Hochzahlen
    s = re.sub(r"\*\*(-?\d+)", lambda m: to_superscript(m.group(1)), s)

    # 2) Wurzeln
    s = s.replace("**0.5", "√")
    s = s.replace("**0.25", "⁴√")

    # 3) 3*x → 3x
    s = re.sub(r"(\d)\*x", r"\1x", s)

    # 4) 2*3 → 2·3
    s = re.sub(r"(\d)\*(\d)", r"\1·\2", s)

    return s

# 👉 Mathe-Eingabe clean machen
transformations = (
    standard_transformations +
    (implicit_multiplication_application, convert_xor)
)

# 👉 Aufgaben

# 👉 Aufgaben

# 🟢 EASY (klassische Schulableitungen)
easy_tasks = [
    x**2 + 3*x,
    2*x**3 - x,
    4*x**2 + 5*x,
    x**4 - x**2,
    6*x + 3,
    7*x**2,
    x**3 + 2*x + 1,
    5*x**4
]

# 🔴 HARD (Mix aus Kettenregel, Produktregel, Quotientenregel, Wurzeln, Brüche, trig)
hard_tasks = [
    (x**2 + 1)*(x**3 - x),                  # Produktregel
    (x**3 + 2*x)/(x**2 + 1),                # Quotientenregel
    (x**2 + 1)**3,                          # Kettenregel
    (x**2 + x)**5,                          # starke Kettenregel
    x* (x**2 + 3)**4,                       # Produkt + Kette
    (x + 1)/(x**3 + 1),                     # Quotient
    x**x,                                    # exponentielle Funktion
    x**2 * (x + 1)**2,                      # gemischt
    (x**2 + 1)**0.5,                        # Wurzel + Kette
    (1 + x**2)**(-1),                      # negative Potenz
]

difficulty = "easy"


current_function = None
correct_answer = None


def new_task():
    global current_function, correct_answer
    if difficulty == "easy":
        current_function = random.choice(easy_tasks)
    else:
        current_function = random.choice(hard_tasks)
    correct_answer = diff(current_function, x)


new_task()


@app.get("/", response_class=HTMLResponse)
def home():
    return """
    <html>
    <head>
        <title>Mathe Trainer</title>

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

            button {
                font-size: 18px;
                padding: 10px 15px;
                margin: 10px;
                border-radius: 8px;
                border: none;
                cursor: pointer;
                background-color: #4a6cf7;
                color: white;
            }

            button:hover {
                background-color: #3557d6;
            }

            #result {
                font-size: 22px;
                margin-top: 20px;
            }
        </style>
    </head>
    
    <body>
        <div id="sidebar">

    <h2>Schwierigkeit</h2>

    <button onclick="setDifficulty('easy')">Einfach</button>
    <button onclick="setDifficulty('hard')">Schwer</button>

    </div>

    <div id="main">

        <h1>📘 Mathe Trainer</h1>
        <div id="difficultyDisplay">Schwierigkeit: Einfach</div>

        <p>Leite ab:</p>
        <div id="task"></div>

        <input id="answer" placeholder="z.B. 2x+3">

        <br>

        <button onclick="check()">Prüfen</button>
        <button onclick="nextTask()">Nächste Aufgabe</button>

        <div id="result"></div>

        <script>

            async function loadTask() {
                let res = await fetch("/task");
                let data = await res.json();
                document.getElementById("task").innerText = data.task;
            }

            async function check() {
                let ans = document.getElementById("answer").value;

                let res = await fetch("/check?answer=" + encodeURIComponent(ans));
                let data = await res.json();

                document.getElementById("result").innerText = data.feedback;
            }

            async function nextTask() {
                await fetch("/next");
                await loadTask();
                document.getElementById("answer").value = "";
                document.getElementById("result").innerText = "";
                answered = false;
                document.getElementById("answer").focus();
            }
            
            async function setDifficulty(level) {

                await fetch("/difficulty?level=" + level);

                document.getElementById("answer").value = "";
                document.getElementById("result").innerText = "";

                if (level === "easy") {
                    document.getElementById("difficultyDisplay").innerText = "Schwierigkeit: Einfach";
                } else {
                    document.getElementById("difficultyDisplay").innerText = "Schwierigkeit: Schwer";
                }

                await loadTask();
}

            let answered = false;
            loadTask();

document.getElementById("answer").addEventListener("keydown", async function(event) {

    if (event.key === "Enter") {

        if (!answered) {

            await check();
            answered = true;

        } else {

            await nextTask();
            answered = false;

        }

    }

});

        </script>
    </div> <!-- closes main -->
    </body>
    </html>
    """


@app.get("/task")
def task():
    return {"task": format_expr(current_function)}


@app.get("/next")
def next_task():
    new_task()
    return {"ok": True}
@app.get("/difficulty")
def set_difficulty(level: str):

    global difficulty

    difficulty = level
    new_task()

    return {"ok": True}


@app.get("/check")
def check(answer: str):

    try:
        user = parse_expr(answer, transformations=transformations)

        if simplify(user - correct_answer) == 0:
            return {"correct": True, "feedback": "✅ Richtig!"}
        else:
            return {
                "correct": False,
                "feedback": "❌ Falsch. Lösung: " + format_expr(correct_answer)
            }

    except:
        return {
            "correct": False,
            "feedback": "⚠ Schreib z.B. 2x+3"
        }
