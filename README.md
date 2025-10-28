# Advanced Python Calculator

A scientific and algebraic desktop calculator built with Python and PySide6. This application features a robust, multi-process architecture to ensure a responsive user interface and separation of concerns between the UI, parsing, and mathematical computation.

## Features

  * **Standard Calculator:** Perform all basic arithmetic operations.
  * **Scientific Functions:** Includes `sin`, `cos`, `tan`, `log`, `√` (sqrt), `e^x`, and the constant `π`.
  * **Algebraic Solver (CAS):** Solves linear equations (e.g., `2*x + 10 = 20`).
  * **Persistent Settings:**
      * **Dark Mode:** Toggle between light and dark themes.
      * **Angle Mode:** Switch between Degrees and Radians for trigonometric functions.
      * **Decimal Precision:** Adjust the number of decimal places for the final output.
  * **Responsive UI:** Uses threading to run complex calculations in the background, preventing the GUI from freezing.
  * **History:** Undo (`↶`) and Redo (`↷`) functionality.
  * **Clipboard:** Paste (`📋`) values from the system clipboard.

## Architecture

This project uses a decoupled, multi-process architecture. The main components are launched as separate subprocesses to isolate their work and ensure the UI remains responsive.

1.  **`main.py` (Launcher)**

      * This is the entry point of the application.
      * It first validates that all required script files (`UI.py`, `MathEngine.py`, etc.) and assets (`config.ini`, `Top_Left_icon.png`) exist.
      * It then launches the `UI.py` script as a new process.

2.  **`UI.py` (Frontend)**

      * This script contains all the PySide6 code for the graphical user interface, including the main window, settings dialog, and all button logic.
      * It manages the application's state (like undo/redo stacks).
      * When a calculation is requested (by pressing `⏎`), it creates a `Worker` thread.
      * This `Worker` thread then calls `MathEngine.py` as a subprocess, passing the user's problem string as an argument. This prevents the UI from freezing during calculation.

3.  **`MathEngine.py` (Core / CAS)**

      * This is the "brain" of the calculator. It receives the raw problem string from `UI.py`.
      * **Tokenizer/Lexer:** The `translator()` function parses the raw string into a list of tokens (numbers, operators, functions, variables).
      * **Parser (AST):** The `ast()` function builds an Abstract Syntax Tree (AST) from the token list using classes like `BinOp`, `Number`, and `Variable`.
      * **Solver:** If the AST is identified as an equation (contains an `=` and a variable), the `solve()` function is used to find the value of the variable.
      * **Evaluator:** If it's a simple expression, the `evaluate()` method is called on the tree.
      * **Delegation:** For scientific functions (like `sin` or `log`), this engine launches *another* subprocess, calling `ScientificEngine.py` to get the result.

4.  **`ScientificEngine.py` (Backend)**

      * This script is a simple, stateless math library.
      * It reads the `config.ini` file to check for the `use_degrees` setting.
      * It accepts a single function string (e.g., `sin(30)`), performs the raw `math` library calculation (correctly converting to radians if needed), and prints the numerical result to `stdout`.

## Project Structure

```
.
├── config.ini          # Stores settings (Dark Mode, Degrees/Radians)
├── README.md           # This file
├── icons/
│   └── Top_Left_icon.png # Application icon
│
└── Python_Scripts/
    ├── main.py           # (Launcher) Validates files and starts UI.py
    ├── UI.py             # (Frontend) All GUI, threading, and settings logic
    ├── MathEngine.py     # (Core) Parser, AST builder, and Solver (CAS)
    └── ScientificEngine.py # (Backend) Performs raw scientific math
```

## Getting Started

### Prerequisites

You must have Python 3 and the PySide6 library installed.

```bash
pip install PySide6
```

### Running the Application

To run the calculator, execute the `main.py` script from the root directory:

```bash
python Python_Scripts/main.py
```

## Configuration

Settings are stored in `config.ini` and can be changed by clicking the `⚙️` icon in the app.

  * `[UI]`
      * `darkmode = True` / `False`: Toggles the dark theme for the UI.
  * `[Scientific_Options]`
      * `use_degrees = True` / `False`: Sets angle mode for `sin`, `cos`, and `tan`. `False` defaults to Radians.
  * `[Math_Options]`
      * `decimal_places = 2`: Sets the number of decimal places for rounding (Note: UI feature, calculation engine prints full float).

## License

This project is licensed under the MIT License.
