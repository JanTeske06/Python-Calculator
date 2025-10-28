# MathEngine.py
import sys
import math
from PySide6 import QtWidgets
from PySide6.QtCore import Qt
import sys
import subprocess
import os
from pathlib import Path
import time
import pickle
import base64
import configparser

rounding = False
cas = False
var_counter = 0
var_list = []
global_subprocess = None
python_interpreter = sys.executable
Operations = ["+","-","*","/","=","^"]
Science_Operations = ["sin","cos","tan","10^x","log","e^", "π", "√"]
ScientificEngine = str(Path(__file__).resolve().parent / "ScientificEngine.py")
config = Path(__file__).resolve().parent.parent / "config.ini"

def ScienceCalculator(problem):
    cmd = [
            python_interpreter,
            ScientificEngine,
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



def isInt(zahl):
    try:
        x = int(zahl)
        return True
    except ValueError:
        return False

def isfloat(zahl):
    try:
        x = float(zahl)
        return True
    except ValueError:
        return False


def isScOp(zahl):
    try:
        return Science_Operations.index(zahl)
    except ValueError:
        return -1


def isOp(zahl):
    try:
        return Operations.index(zahl)
    except ValueError:
        return -1


def isolate_bracket(problem, b_anfang):
    start = b_anfang
    start_klammer_index = problem.find('(', start)
    if start_klammer_index == -1:
        raise SyntaxError("Fehlende öffnende Klammer nach Funktionsnamen.")
    b = start_klammer_index + 1
    bracket_count = 1
    while bracket_count != 0 and b < len(problem):
        if problem[b] == '(':
            bracket_count += 1
        elif problem[b] == ')':
            bracket_count -= 1
        b += 1
    ergebnis = problem[start:b]
    return (ergebnis, b)

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


def translator(problem):
    global var_counter
    global var_list
    var_list = [None] * len(problem)
    problemlength = len(problem)
    full_problem = []
    b = 0

    while b < problemlength:

        current_char = problem[b]

        if isInt(current_char):
            str_number = current_char
            hat_schon_komma = False  

            while (b + 1 < problemlength) and (isInt(problem[b + 1]) or problem[b + 1] == "."):

                if problem[b + 1] == ".":
                    if hat_schon_komma:
                        raise SyntaxError("Doppeltes Kommazeichen.")
                    hat_schon_komma = True

                b += 1
                str_number += problem[b]

            if isfloat(str_number):
                full_problem.append(float(str_number))
            else:
                full_problem.append(int(str_number))

        elif isOp(current_char) != -1:
            full_problem.append(current_char)

        elif current_char == " ":
            pass

        elif current_char == "(":
            full_problem.append("(")

        elif current_char == ")":
            full_problem.append(")")

        elif current_char == ",":
            full_problem.append(",")
            
        # elif(current_char) in Science_Operations:
        #     full_problem.append(ScienceCalculator(current_char))

        elif ((((current_char) == 's' or (current_char) == 'c' or (current_char) == 't' or (
        current_char) == 'l') and problemlength - b >= 5) or
              (current_char == '√' and problemlength - b >= 2) or
              (current_char == 'e' and problemlength - b >= 3)):

            if(current_char == '√' and problem[b+1] == '('):
                full_problem.append('√')
                full_problem.append('(')
                b=b+1
            elif(current_char == 'e' and problem[b+1] == '^'and problem[b+2] == '('):
                full_problem.append('e^')
                full_problem.append('(')
                b=b+2

            elif (current_char in ['s', 'c', 't', 'l'] and len(problem)>=3 and problem[b + 3] == '('):

                if problem[b:b + 3] in ['sin', 'cos', 'tan', 'log']:
                    full_problem.append(problem[b:b + 3])
                    full_problem.append('(')
                    b += 3


        elif current_char == 'π':
                ergebnis_string = ScienceCalculator('π')
                try:
                    berechneter_wert = float(ergebnis_string)
                    full_problem.append(berechneter_wert)
                except ValueError:
                    raise ValueError(f"Fehler bei Konstante π: {ergebnis_string}")


        else:
            if current_char in var_list:
                full_problem.append("var" + str(var_list.index(current_char)))
            else:
                full_problem.append("var" + str(var_counter))
                var_list[var_counter] = current_char
                var_counter += 1

        b = b + 1

    b = 0
    while b < len(full_problem):

        if b + 1 < len(full_problem):

            aktuelles_element = full_problem[b]
            nachfolger = full_problem[b + 1]
            einfuegen_noetig = False

            ist_funktionsname = isScOp(nachfolger) != -1
            ist_zahl_oder_variable = isinstance(aktuelles_element, (int, float)) or "var" in str(aktuelles_element)
            ist_klammer_oder_nachfolger = nachfolger == '(' or "var" in str(nachfolger) or isinstance(nachfolger,
                                                                                                      (int,
                                                                                                       float)) or ist_funktionsname
            ist_kein_operator = aktuelles_element not in Operations and nachfolger not in Operations

            if (ist_zahl_oder_variable or aktuelles_element == ')') and \
                    (ist_klammer_oder_nachfolger or nachfolger == '(') and \
                    ist_kein_operator:

                if aktuelles_element in ['*', '+', '-', '/'] or nachfolger in ['*', '+', '-', '/']:
                    einfuegen_noetig = False
                elif aktuelles_element == ')' and nachfolger == '(':
                    einfuegen_noetig = True
                elif aktuelles_element != '(' and nachfolger != ')':
                    einfuegen_noetig = True

            if einfuegen_noetig:
                full_problem.insert(b + 1, '*')

        b += 1

    return full_problem


def ast(received_string):
    global cas
    analysed = translator(received_string)
    if global_subprocess == "0":
        print(analysed)


    def parse_factor(tokens):
        token = tokens.pop(0)
        if token == "(":
            baum_in_der_klammer = parse_sum(tokens)

            if not tokens or tokens.pop(0) != ')':
                raise SyntaxError("Fehlende schließende Klammer ')'")

            return baum_in_der_klammer

        elif token in Science_Operations:

            if token == 'π':
                ScienceOp = 'π'
                ergebnis = ScienceCalculator(ScienceOp)

                try:
                    berechneter_wert = float(ergebnis)
                    return Number(berechneter_wert)
                except ValueError:
                    raise SyntaxError(f"Fehler bei Konstante π: {ergebnis}")

            else:
                if not tokens or tokens.pop(0) != '(':
                    raise SyntaxError(f"Fehlende öffnende Klammer nach Funktion {token}")

                argument_baum = parse_sum(tokens)

                if token == 'log' and tokens and tokens[0] == ',':
                    tokens.pop(0)
                    basis_baum = parse_sum(tokens)
                    if not tokens or tokens.pop(0) != ')':
                        raise SyntaxError(f"Fehlende schließende Klammer nach Logarithmusbasis.")
                    argument_wert = argument_baum.evaluate()
                    basis_wert = basis_baum.evaluate()
                    ScienceOp = f"{token}({argument_wert},{basis_wert})"
                else:
                    if not tokens or tokens.pop(0) != ')':
                        raise SyntaxError(f"Fehlende schließende Klammer nach Funktion {token}")

                    argument_wert = argument_baum.evaluate()
                    ScienceOp = f"{token}({argument_wert})"
                ergebnis_string = ScienceCalculator(ScienceOp)
                try:
                    berechneter_wert = float(ergebnis_string)
                    return Number(berechneter_wert)
                except ValueError:
                    raise SyntaxError(f"Fehler bei wissenschaftlicher Funktion: {ergebnis_string}")


        elif isInt(token):
            return Number(token)

        elif isfloat(token):
            return Number(token)

        elif "var" in str(token):
            return Variable(token)

        else:
            raise SyntaxError(f"Unerwartetes Token: {token}")

        # NEUE FUNKTION: Behandelt unäre Operatoren (+, -)

    def parse_unary(tokens):
            if tokens and tokens[0] in ('+', '-'):
                operator = tokens.pop(0)
                operand = parse_unary(tokens)

                if operator == '-':
                    if isinstance(operand, Number):
                        return Number(-operand.evaluate())
                    return BinOp(Number(0.0), '-', operand)
                else:
                    return operand
            return parse_power(tokens)

    def parse_power(tokens):
        aktueller_baum = parse_factor(tokens)
        while tokens and tokens[0] in ("^"):
            operator = tokens.pop(0)
            rechtes_teil = parse_unary(tokens)
            if not isinstance(aktueller_baum, Variable) and not isinstance(rechtes_teil, Variable):
                basis = aktueller_baum.evaluate()
                exponent = rechtes_teil.evaluate()
                ergebnis = basis ** exponent
                aktueller_baum = Number(ergebnis)
            else:
                aktueller_baum = BinOp(aktueller_baum, operator, rechtes_teil)
        return aktueller_baum


    def parse_term(tokens):

        aktueller_baum = parse_unary(tokens)
        while tokens and tokens[0] in ("*","/"):
            operator = tokens.pop(0)
            rechtes_teil = parse_unary(tokens)
            aktueller_baum = BinOp(aktueller_baum, operator, rechtes_teil)

        return aktueller_baum



    def parse_sum(tokens):

        aktueller_baum = parse_term(tokens)

        while tokens and tokens[0] in ("+", "-"):

            operator = tokens.pop(0)
            if debug == 1:
                print("Currently at:" + str(operator) + "in parse_sum")
            rechte_seite = parse_term(tokens)
            aktueller_baum = BinOp(aktueller_baum, operator, rechte_seite)

        return aktueller_baum

    def parse_gleichung(tokens):
        linke_seite = parse_sum(tokens)
        if tokens and tokens[0] == "=":
            operator = tokens.pop(0)
            rechte_seite = parse_sum(tokens)

            return BinOp(linke_seite, operator, rechte_seite)
        return linke_seite

    finaler_baum = parse_gleichung(analysed)

    if isinstance(finaler_baum, BinOp) and finaler_baum.operator == '=' and var_counter >= 1:
        cas = True

    if global_subprocess == "0":
        print("Finaler AST:")
        print(finaler_baum)

    return finaler_baum


def solve(baum,var_name):
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


def cleanup(ergebnis):
    global rounding
    cfg = configparser.ConfigParser()
    cfg.read(config, encoding='utf-8')
    try:
        decimals = cfg.get('Math_Options', 'decimal_places', fallback='2')

    except (configparser.NoSectionError, configparser.NoOptionError):
        decimals = 2


    if isinstance(ergebnis, (int, float)):
        if ergebnis == int(ergebnis):
            return int(ergebnis)
        else:
            s_ergebnis = str(ergebnis)
            if '.' in s_ergebnis:
                decimal_index = s_ergebnis.find('.')
                number_of_decimals = len(s_ergebnis) - decimal_index - 1

                if number_of_decimals > int(decimals):
                    rounding = True
                    new_number = round(float(ergebnis),int(decimals))
                    #print(new_number)
                    ergebnis = new_number
                elif number_of_decimals == int(decimals):
                    return ergebnis

                elif number_of_decimals <= int(decimals):
                    return ergebnis

                return ergebnis
            return ergebnis
    return ergebnis





def main():
    global global_subprocess, var_counter, var_list
    var_counter = 0
    var_list = []

    if len(sys.argv) > 1:
        received_string = sys.argv[1]
        global_subprocess = "1"
    else:
        global_subprocess = "0"
        print("Gebe das Problem ein: ")
        received_string = input()

    try:
        finaler_baum = ast(received_string)
        if cas and var_counter > 0:
            var_name_in_ast = "var0"
            ergebnis = solve(finaler_baum, var_name_in_ast)
        elif not cas and var_counter == 0:
            ergebnis = finaler_baum.evaluate()
        else:
            if global_subprocess == "0":
                print(
                    "FEHLER: Der Solver wurde auf einer Nicht-Gleichung oder der Taschenrechner auf einer Gleichung aufgerufen.")
            return


        ergebnis = cleanup(ergebnis)
        ungefaehr_zeichen = "\u2248"

        if global_subprocess == "0":
            variable_name = var_list[0] if var_list else "Ergebnis"
            print(f"Das Ergebnis der Berechnung ist: {variable_name} = {ergebnis}")

        elif cas ==True and rounding == True:
            print(f"x {ungefaehr_zeichen}" + str(ergebnis))

        elif cas ==True:
            print("x = " + str(ergebnis))

        elif rounding ==True:
            print(f"{ungefaehr_zeichen} " + str(ergebnis))

        else:
            print("= " + str(ergebnis))


    except (ValueError, SyntaxError, ZeroDivisionError) as e:
        print(f"FEHLER: {e}")
    except Exception as e:
        print(f"UNERWARTETER FEHLER: {e}")


if __name__ == "__main__":
    debug = 0  # 1 = activated, 0 = deactivated
    #time.sleep(100)
    main()
