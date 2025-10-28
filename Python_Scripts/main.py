#main.py
import subprocess
import sys
import os
from pathlib import Path

python_interpreter = sys.executable


UI = Path(__file__).resolve().parent / "UI.py"
Main = Path(__file__).resolve().parent / "Main.py"
ScientificEngine = Path(__file__).resolve().parent / "ScientificEngine.py"
config = Path(__file__).resolve().parent.parent / "config.ini"
icon = Path(__file__).resolve().parent.parent / "icons" / "icon.png"


def check_files_exist():
    REQUIRED = [
        UI,
        Main,
        ScientificEngine,
        config,
        icon
    ]

    missing_files = []
    b = 0
    while b < len(REQUIRED):
        current_path = REQUIRED[b]
        if not current_path.exists():
            missing_files.append(current_path.name)
        b+=1

    if missing_files:
        print("Fehler: Folgende Dateien fehlen:")
        for file in missing_files:
            print(f"- {file}")
        sys.exit(1)

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
    check_files_exist()
    main()
