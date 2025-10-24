import subprocess
import sys
import os
from pathlib import Path

UI = str(Path(__file__).resolve().parent / "UI.py")
python_interpreter = sys.executable

def UICalc():
    cmd = [
            python_interpreter,
            UI
    ]
    try:
        ergebnis = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True)
        zurueckgeschickter_string = ergebnis.stdout.strip()
        return zurueckgeschickter_string
    except subprocess.CalledProcessError as e:
        print(f"Ein Fehler ist aufgetreten: {e}")

def main():
    UICalc()


if __name__ == "__main__":
    debug = 0  # 1 = activated, 0 = deactivated
    main()
