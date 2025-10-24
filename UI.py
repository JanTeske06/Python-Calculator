from PySide6 import QtWidgets
from PySide6.QtCore import Qt
import sys
import subprocess
import os
from pathlib import Path

CalcSmplfd = str(Path(__file__).resolve().parent / "CalcSmplfd.py")
python_interpreter = sys.executable
history = ["0"]
history_index = 0

def Calc(problem):
    cmd = [
        python_interpreter,
        CalcSmplfd,
        problem
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


class CalculatorPrototype(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Taschenrechner Prototyp")
        self.resize(300, 450)

        main_v_layout = QtWidgets.QVBoxLayout(self)

        # Display (Stretch 1)
        self.display = QtWidgets.QLineEdit("0")
        self.display.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.display.setReadOnly(True)
        font = self.display.font()
        font.setPointSize(24)
        self.display.setFont(font)
        main_v_layout.addWidget(self.display, 1)

        button_container = QtWidgets.QWidget()
        main_v_layout.addWidget(button_container, 4)

        button_grid = QtWidgets.QGridLayout(button_container)

        button_grid.setSpacing(0)
        button_grid.setContentsMargins(0, 0, 0, 0)

        for i in range(6):  # vertikal
            button_grid.setRowStretch(i, 1)
        for j in range(4):  # horizental
            button_grid.setColumnStretch(j, 1)

        expanding_policy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Policy.Expanding,
            QtWidgets.QSizePolicy.Policy.Expanding
        )

        buttons = [
            ('f', 0, 0), ('↷', 0, 1), ('↶', 0, 2), ('<', 0, 3),
            ('x', 1, 0), ('X', 1, 1), ('X', 1, 2), ('/', 1, 3),
            ('7', 2, 0), ('8', 2, 1), ('9', 2, 2), ('*', 2, 3),
            ('4', 3, 0), ('5', 3, 1), ('6', 3, 2), ('-', 3, 3),
            ('1', 4, 0), ('2', 4, 1), ('3', 4, 2), ('+', 4, 3),
            ('C', 5, 0), ('0', 5, 1), ('=', 5, 2), ('⏎', 5, 3)  #
            # --------------------------------------------------------------------------------------
        ]
        for text, row, col in buttons:
            button = QtWidgets.QPushButton(text)

            button.setSizePolicy(expanding_policy)
            button.clicked.connect(lambda checked=False, val=text: self.handle_button_press(val))
            button_grid.addWidget(button, row, col)

    def handle_button_press(self, value):
        global history
        global history_index
        current_text = self.display.text()

        if value == 'C':
            self.display.setText("0")
            self.history_back = ["0"] * 15
            self.history_forw = [""] * 15
            return

        elif (value == '<'):
            if len(current_text) <= 1 or current_text == "0":
                self.display.setText("0")
                return
            new_text = current_text[:-1]
            self.display.setText(new_text)
            return

        elif value == '⏎':
            ergebnis = Calc(current_text)
            if ergebnis == "True":
                current_text =  (ergebnis + "    " + current_text)
                print(f"Ergebnis: {ergebnis}")
            elif ergebnis == "False":
                current_text =  (ergebnis + "    " + current_text)
                print(f"Ergebnis: {ergebnis}")
            else:
                current_text = ergebnis

        elif value == '↶':
            if history_index > 0:
                history_index -= 1
                current_text = history[history_index]
                self.display.setText(current_text)
                print(f"Es wurde die Taste '{value}' gedrückt.")
            return


        elif value == '↷':
            neuer_index = history_index + 1
            if neuer_index < len(history) and history[neuer_index] != "":
                history_index = neuer_index
                current_text = history[history_index]
                self.display.setText(current_text)
                print(f"Es wurde die Taste '{value}' gedrückt.")
            return


        else:
            if current_text == "0":
                current_text = ""
            current_text += str(value)

        self.display.setText(current_text)
        history.insert(history_index,current_text)
        history_index +=1

        print(f"Es wurde die Taste '{value}' gedrückt.")


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = CalculatorPrototype()
    window.show()
    sys.exit(app.exec())
