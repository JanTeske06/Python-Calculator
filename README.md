MULTI-PROCESS PYTHON CALCULATOR
===============================

---
OVERVIEW
---

This project is an advanced desktop calculator application developed using PySide6. Its primary feature is not just the calculation itself, but its unique multi-process architecture.

Instead of a monolithic design, this application deliberately utilizes Python's subprocess module to manage different components (UI, standard calculation, and scientific calculation) as separate, communicating processes. This approach demonstrates a practical understanding of inter-process communication (IPC), process isolation, and modular system design.

The core logic features a custom-built recursive descent parser that constructs an Abstract Syntax Tree (AST) to correctly evaluate mathematical expressions, respecting the order of operations.

---
KEY FEATURES
---

* Modular IPC Architecture: The UI, core logic, and scientific functions run as distinct processes, communicating via standard I/O streams.

* Custom Expression Parser:
    - Tokenizer (translator): A custom lexer that scans the raw input string and converts it into a list of logical tokens (e.g., numbers, operators, parentheses).
    - AST Parser (ast): A recursive descent parser that builds an Abstract Syntax Tree (AST) from the token stream.
    - Evaluator: A function that traverses the AST to compute the final result, naturally enforcing the order of operations (PEMDAS/BODMAS).

* Rich GUI with PySide6: A clean, responsive user interface featuring a display, a full grid of buttons, and history navigation.

* Mathematical Capabilities:
    - Full support for standard arithmetic: +, -, *, /, ^ (power).
    - Correctly handles nested parentheses ().
    - Supports implicit multiplication (e.g., 5(2+3) is evaluated as 5*(2+3)).
    - Handles scientific functions (e.g., sin, cos, tan, log) and constants (π).
    - Evaluates boolean equations (e.g., 5+5=10 returns True).

* Input History: Navigate through previous calculations using the ↶ (undo) and ↷ (redo) buttons.

---
TECHNICAL ARCHITECTURE
---

The application is intentionally decoupled into four distinct Python scripts, each with a specific role.

1. calc.py (Entry Point)
   - The main bootstrap script.
   - Its sole responsibility is to launch the main user interface (Ui.py) as a new child process.

2. Ui.py (User Interface - The "Client")
   - Manages the entire PySide6 GUI, including window layout, button connections, and display updates.
   - It captures user input. Upon pressing "Enter" (⏎), it does not perform the calculation itself.
   - It spawns CalcSmplfd.py as a new subprocess, passing the user's expression as a command-line argument.
   - It then waits for, captures, and displays the stdout from the child process as the result.

3. CalcSmplfd.py (Core Logic - The "Parsing Service")
   - This is the "brain" of the operation. It receives the raw expression string from Ui.py.
   - Tokenizer: The 'translator' function sanitizes and tokenizes the input string.
   - Sub-process Delegation: When it encounters a scientific function (like sin(...) or log(...)), it delegates this specific task by spawning ScienceCalc.py as another subprocess. It waits for the result (e..g, 0.5) and substitutes it back into its token list.
   - AST Construction: The 'ast' function builds the Abstract Syntax Tree.
   - Evaluation: The 'evaluate' method on the final tree node computes the result.
   - The final result is printed to stdout, which is then read by Ui.py.

4. ScienceCalc.py (Scientific Engine - The "Microservice")
   - A specialized, single-purpose script that wraps Python's 'math' module.
   - It accepts a single scientific function string (e.g., "sin(30)", "log(100,10)"), performs the calculation, and prints the result to stdout.

Data Flow Example (User inputs 5*sin(30))
------------------------------------------

1. User runs python calc.py.
2. calc.py launches Ui.py.
3. User types 5*sin(30) into the GUI and presses ⏎.
4. Ui.py spawns CalcSmplfd.py, passing the string "5*sin(30)".
5. CalcSmplfd.py tokenizes the string to [5, '*', 'sin(30)'].
6. When it processes 'sin(30)', it spawns ScienceCalc.py, passing "sin(30)".
7. ScienceCalc.py computes math.sin(math.radians(30)), gets 0.5, and print(0.5).
8. CalcSmplfd.py reads the 0.5 from the subprocess's stdout and continues parsing, now with the token list [5, '*', 0.5].
9. It builds the AST, evaluates it to 2.5, and print(2.5).
10. Ui.py reads the 2.5 from CalcSmplfd.py's stdout and updates the display.

---
HOW TO RUN
---

Prerequisites
-------------
* Python 3.x
* PySide6

Installation & Launch
---------------------

1. Clone this repository (or ensure all four .py files are in the same directory).

2. Install the required package:
   pip install PySide6

3. Run the main application script:
   python calc.py

---
PROJECT STATUS
---
60%
This project is a functional prototype. Several UI buttons (marked with 'x') are placeholders, and scientific functions must be typed manually. The core focus was on building and demonstrating the robust backend architecture and custom parser.
