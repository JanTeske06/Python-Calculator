# Calculator Prototype

## Project Overview

This project is a prototype for a scientific calculator developed in Python. It features a graphical user interface (GUI) built with PySide6 and a custom backend for parsing and evaluating mathematical expressions.

A key characteristic of this project is its architecture, which relies heavily on `subprocess` calls to programmatically decouple the GUI from the core calculation logic.

---

## Features

* **Graphical User Interface (GUI)**: Implemented using PySide6.
* **Standard Arithmetic**: Supports addition (`+`), subtraction (`-`), multiplication (`*`), division (`/`), and exponentiation (`^`).
* **Scientific Functions**: Includes `sin()`, `cos()`, `tan()`, `log()`, and `√()` (square root).
* **Constants**: Provides `π` (Pi) and `e` (Euler's number).
* **Basic CAS (Computer Algebra System)**: Capable of solving linear equations with a single variable (e.g., `"2*x + 1 = 5"`).
* **Implicit Multiplication**: Automatically detects and processes inputs such as `"5x"` or `"2(3+1)"` as multiplication.
* **Input History**: Allows navigation through previous entries using the `↶` (undo) and `↷` (redo) buttons.

---

## Architecture and File Structure

The project is divided into four primary files that communicate via subprocesses. This modular structure enforces a strict separation of concerns between the user interface and the backend logic.



* **`main.py`**
    * This is the main entry point for the application. Its sole responsibility is to launch `UI.py` in a separate subprocess.

* **`UI.py`**
    * Defines the complete graphical user interface (GUI) using PySide6.
    * It captures all button inputs and displays them. Upon pressing the "Enter" key (`⏎`), it passes the entire calculation string as an argument to a new subprocess executing `CalcSmplfd.py` and awaits its standard output.

* **`CalcSmplfd.py` (Core Calculator Engine)**
    * This script is the "brain" of the calculator. It operates as a pure command-line script that accepts a single string as input.
    * **1. Tokenizer (`translator`):** Deconstructs the input string into a list of tokens (e.g., `"5x+1"` becomes `[5.0, '*', 'var0', '+', 1.0]`).
    * **2. AST Parser (`ast`):** Constructs an Abstract Syntax Tree (AST) from the token list. This tree represents the mathematical structure of the input, respecting the order of operations (e.g., PEMDAS).
    * **3. Solver / Evaluator:**
        * **CAS Mode:** If the input is an equation with a variable (e.g., `5*x+1=11`), the `solve()` function is invoked to find the linear solution.
        * **Standard Mode:** If the input is a standard term (e.g., `5+3*2`), the `evaluate()` function is called to compute the result.
    * **4. Scientific Sub-processing:** When the tokenizer identifies a scientific function (like `sin(...)` or `log(...)`), it calls `ScienceCalc.py` in *another* subprocess to compute only that specific part.
    * The final result is sent to standard output via `print()`, which is then read by `UI.py` and displayed to the user.

* **`ScienceCalc.py`**
    * A specialized helper script dedicated to performing individual scientific calculations (e.g., `math.sin(1.5)` or `math.log(10, 2)`) passed as arguments.
    * It utilizes Python's `math` library and returns the result via `print()` to its parent process (`CalcSmplfd.py`).

---

## Requirements

* Python 3.x
* PySide6

The required library can be installed using pip:

```bash
pip install PySide6
