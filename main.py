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

def format_expr(expr):
    return str(expr).replace("*", "").replace("**", "^")

# 👉 Mathe-Eingabe clean machen
transformations = (
    standard_transformations +
    (implicit_multiplication_application, convert_xor)
)

# 👉 Aufgaben
aufgaben = [
    x**2 + 3*x,
    x**3 - 2*x,
    4*x**2 + x,
    x**4 - x**2,
    5*x**3 + 2*x
]

current_function = None
correct_answer = None


def new_task():
    global current_function, correct_answer
    current_function = random.choice(aufgaben)
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

        <h1>📘 Mathe Trainer</h1>

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
            }

            loadTask();

        </script>

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
