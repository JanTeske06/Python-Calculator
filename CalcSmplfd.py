import sys
import math


global_subprocess = None

Operations = ["+","-","*","/","="]
Science_Operations = ["sin","cos","tan","10^x","log","e"]

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



def isOp(zahl):
    try:
        index_position = Operations.index(zahl)
        if index_position == 0:
            return index_position
        elif index_position == 1:
            return index_position
        elif index_position == 2:
            return index_position
        elif index_position == 3:
            return index_position
        elif index_position == 4:
            return index_position
    except ValueError:
        return -1


def translator(problem):
    var_counter = 0
    problemlength = len(problem)
    full_problem = []
    b = 0
    var_list = [None] * len(problem)

    while b < problemlength:

        current_char = problem[b]

        if isInt(current_char):
            str_number = current_char

            while (b + 1 < problemlength) and (isInt(problem[b + 1]) or problem[b + 1] == "."):
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

            ist_zahl_oder_variable = isinstance(aktuelles_element, (int, float)) or "var" in str(aktuelles_element)
            ist_klammer_oder_nachfolger = nachfolger == '(' or "var" in str(nachfolger) or isinstance(nachfolger,
                                                                                                      (int, float))
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
    analysed = translator(received_string)
    if global_subprocess == "0":
        print(analysed)

    class Number:
        def __init__(self,value):
            self.value = float(value)
        def evaluate(self):
            return self.value

        def __repr__(self):
            return f"Nummer({self.value})"

    class Variable:
        def __init__ (self,name):
            self.name = name
        def evaluate(self):
            raise SyntaxError("Fehlender Solver.")
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
            elif self.operator == '/':
                if right_value == 0:
                    raise ZeroDivisionError("Teilen durch Null")
                return left_value / right_value
            elif self.operator == '=':
                return left_value == right_value
            else:
                raise ValueError(f"Unbekannter Operator: {self.operator}")

        def __repr__(self):
            return f"BinOp({self.operator!r}, left={self.left}, right={self.right})"



    def parse_factor(tokens):
        token = tokens.pop(0)
        if debug == 1:
            print("Currently at:" + str(token) + "in parse_factor")

        if token == "(":
            baum_in_der_klammer = parse_sum(tokens)

            if not tokens or tokens.pop(0) != ')':
                raise SyntaxError("Fehlende schließende Klammer ')'")

            return baum_in_der_klammer

        elif isInt(token):
            return Number(token)

        elif isfloat(token):
            return Number(token)

        elif "var" in str(token):
            return Variable(token)

        else:
            raise SyntaxError(f"Unerwartetes Token: {token}")




    def parse_term(tokens):

        aktueller_baum = parse_factor(tokens)
        while tokens and tokens[0] in ("*","/"):
            operator = tokens.pop(0)
            rechtes_teil = parse_factor(tokens)
            aktueller_baum = BinOp(aktueller_baum, operator, rechtes_teil)

        return aktueller_baum



    def parse_sum(tokens):

        aktueller_baum = parse_term(tokens)

        while tokens and tokens[0] in ("+","-"):

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
    if global_subprocess == "0":
        print("Finaler AST:")
        print(finaler_baum)
    return finaler_baum


def main():
    global global_subprocess
    if len(sys.argv) > 1:
        received_string = sys.argv[1]
        global_subprocess = "1"


    else:
        global_subprocess = "0"
        print("Gebe das Problem ein: ")
        received_string = input()

    finaler_baum = ast(received_string)

    try:
        ergebnis = finaler_baum.evaluate()
        if global_subprocess == "0":
            print(f"Das Ergebnis der Berechnung ist: {ergebnis}")
        else:
            print(ergebnis)

    except (ValueError, SyntaxError, ZeroDivisionError) as e:  # (Alle Fehler fangen)
        print(f"Fehler: {e}")

if __name__ == "__main__":
    debug = 0  # 1 = activated, 0 = deactivated
    main()
