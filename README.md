# Calculator Prototype

## Project Overview

This is a prototype for a scientific calculator developed in Python. It features a graphical user interface (GUI) built with PySide6 and a custom backend for parsing and evaluating mathematical expressions.

A key feature of this project is its multi-process architecture. The user interface, the core logic (parser/solver), and the scientific calculations are split into separate scripts that communicate via `subprocess` calls.

---

## 🚀 Features

* **Graphical User Interface (GUI)**: Implemented using PySide6.
* **Standard Arithmetic**: Supports `+`, `-`, `*`, `/`, and `^` (exponentiation).
* **Scientific Functions**: Includes `sin()`, `cos()`, `tan()`, `log()`, `√()` (square root), and the constants `π` and `e`.
* **Configurable Angle Units**: A settings menu (⚙️) allows switching between **Degrees** and **Radians** for trigonometric functions. The setting is saved in `config.ini`.
* **Undo/Redo System**: A robust two-stack system allows for undoing (`↶`) and redoing (`↷`) inputs.
* **Linear CAS (Computer Algebra System)**: Capable of solving linear equations with a single variable (e.g., `"5*(2x - 3) = 0.5*(x + 10)"`).
* **Implicit Multiplication**: Automatically detects inputs like `"5x"` or `"2(3+1)"` as multiplication.
* **Startup Validation**: `main.py` verifies that all required script and configuration files are present before launching.

---

## 🛠️ Architecture and File Structure

The project is divided into a chain of subprocesses to ensure a clear separation of concerns.



* **`main.py` (The Launcher)**
    * This is the main entry point for the application.
    * It first checks if all required files (`UI.py`, `MathEngine.py`, `ScientificEngine.py`, `config.ini`) exist.
    * Its sole responsibility is to launch `UI.py` in a separate subprocess.

* **`UI.py` (The Frontend)**
    * Defines the entire graphical user interface (GUI) using PySide6.
    * Includes the `SettingsDialog`, which **writes** to the `config.ini` file.
    * Manages the Undo/Redo system (using the global lists `undo` and `redo`).
    * Captures all button inputs.
    * When a calculation is triggered (`⏎`), it passes the entire input string to a subprocess running `MathEngine.py`.

* **`MathEngine.py` (The Brain / Core Logic)**
    * This is the core parser and solver, operating as a pure command-line script.
    * **Tokenizer (`translator`):** Deconstructs the input string into a list of tokens (e.g., `"5x+1"` becomes `[5.0, '*', 'var0', '+', 1.0]`).
    * **AST Parser (`ast`):** Builds an Abstract Syntax Tree (AST) from the tokens to represent the mathematical structure (i.e., order of operations).
    * **Solver / Evaluator:**
        * **CAS Mode:** Solves linear equations (`solve()`).
        * **Standard Mode:** Evaluates standard expressions (`evaluate()`).
    * When it encounters a scientific function (e.g., `sin(...)` or `π`), it calls `ScientificEngine.py` in *another* subprocess to compute only that part.

* **`ScientificEngine.py` (The Specialist Engine)**
    * A specialized helper script that only performs individual scientific calculations (e.g., `math.sin(...)` or `math.log(...)`).
    * It **reads** the `config.ini` on startup (`settings_load()`) to determine whether to operate in degree or radian mode.
    * It returns the raw numerical result via `print()` to `MathEngine.py`.

* **`config.ini` (The Configuration File)**
    * Acts as a simple data store to share settings (like `use_degrees`) between processes.
    * It is **written** by `UI.py` and **read** by `ScientificEngine.py`.

---

## 📋 Requirements

* Python 3.x
* PySide6

You can install the required library using pip:
```bash
pip install PySide6
