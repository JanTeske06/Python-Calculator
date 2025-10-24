import sys
import math
from PySide6 import QtWidgets
from PySide6.QtCore import Qt
import sys
import subprocess
import os
from pathlib import Path
import time


#Basis Konzept: A*x + B = C*x + D
# x = (D - B) / (A - C

class Number:
    def __init__(self, value):
        self.value = float(value)

    def evaluate(self):
        return self.value

    def collect_term(self, var_name):
        return (0, self.value)

    def __repr__(self):
        return f"Nummer({self.value})"


class Variable:
    def __init__(self, name):
        self.name = name

    def evaluate(self):
        raise SyntaxError("Fehlender Solver.")

    def collect_term(self, var_name):
        if self.name == var_name:
            return (1, 0)
        else:
            raise ValueError(f"Mehrere Variablen gefunden: {self.name}")
            return (0, 0)

    def __repr__(self):
        return f"Variable('{self.name}')"


class BinOp:
    def __init__(self, left, operator, right):
        self.left = left
        self.operator = operator
        self.right = right

    def evaluate(self):
        left_value = self.left.evaluate()
        right_value = self.right.evaluate()

        if self.operator == '+':
            return left_value + right_value
        elif self.operator == '-':
            return left_value - right_value
        elif self.operator == '*':
            return left_value * right_value
        elif self.operator == '^':
            return left_value ** right_value
        elif self.operator == '/':
            if right_value == 0:
                raise ZeroDivisionError("Teilen durch Null")
            return left_value / right_value
        elif self.operator == '=':
            return left_value == right_value
        else:
            raise ValueError(f"Unbekannter Operator: {self.operator}")

    def collect_term(self, var_name):
        (left_faktor, left_konstante) = self.left.collect_term(var_name)
        (right_faktor, right_konstante) = self.right.collect_term(var_name)

        if self.operator == '+':
            result_faktor = left_faktor + right_faktor
            result_konstante = left_konstante + right_konstante
            return (result_faktor, result_konstante)

        elif self.operator == '-':
            result_faktor = left_faktor - right_faktor
            result_konstante = left_konstante - right_konstante
            return (result_faktor, result_konstante)

        elif self.operator == '*':
            if left_faktor != 0 and right_faktor != 0:
                raise SyntaxError("x^x Fehler.")

            elif left_faktor == 0:
                result_faktor = left_konstante * right_faktor
                result_konstante = left_konstante * right_konstante
                return (result_faktor, result_konstante)

            elif right_faktor == 0:
                result_faktor = right_konstante * left_faktor
                result_konstante = right_konstante * left_konstante
                return (result_faktor, result_konstante)

            elif left_faktor == 0 and right_faktor == 0:
                result_faktor = 0
                result_konstante = right_konstante * left_konstante
                return (result_faktor, result_konstante)


        elif self.operator == '/':
            if right_faktor != 0:
                raise ValueError("Nicht lineare Gleichung. (Teilen durch x)")
            elif right_konstante == 0:
                raise ZeroDivisionError("Solver: Teilen durch Null")
            else:
                result_faktor = left_faktor / right_konstante
                result_konstante = left_konstante / right_konstante
                return (result_faktor, result_konstante)




        elif self.operator == '^':
            raise ValueError("Potenzen werden vom linearen Solver nicht unterstützt.")


        elif self.operator == '=':
            raise ValueError("Sollte nicht passieren: '=' innerhalb von collect_terms")

        else:
            raise ValueError(f"Unbekannter Operator: {self.operator}")

    def __repr__(self):
        return f"BinOp({self.operator!r}, left={self.left}, right={self.right})"
import sys
import math
from PySide6 import QtWidgets
from PySide6.QtCore import Qt
import sys
import subprocess
import os
from pathlib import Path
import time

global_subprocess = None
python_interpreter = sys.executable
Operations = ["+", "-", "*", "/", "=", "^"]
Science_Operations = ["sin", "cos", "tan", "10^x", "log", "e", "π"]
ScienceCalc = str(Path(__file__).resolve().parent / "ScienceCalc.py")






def solve(baum, var_name):
    if not isinstance(baum, BinOp) or baum.operator != '=':
        raise ValueError("Keine gültige Gleichung zum Lösen.")
    (A, B) = baum.left.collect_term(var_name)
    (C, D) = baum.right.collect_term(var_name)
    nenner = A - C
    zaehler = D - B
    if nenner == 0:
        if zaehler == 0:
            return "Unendlich viele Lösungen"
        else:
            return "Keine Lösung"
    return zaehler / nenner



def main():
    global global_subprocess
    if len(sys.argv) > 1:
        received_string = sys.argv[1]
        global_subprocess = "1"


    else:
        global_subprocess = "0"
        print("Gebe das Problem ein: ")
        received_string = input()

    try:

        ergebnis = solve(received_string, "var0")
        if global_subprocess == "0":
            print(f"Das Ergebnis der Berechnung ist: {ergebnis}")
        else:
            print(ergebnis)


    except (ValueError, SyntaxError, ZeroDivisionError) as e:
        print(f"FEHLER: {e}")


if __name__ == "__main__":
    debug = 0  # 1 = activated, 0 = deactivated
    main()
