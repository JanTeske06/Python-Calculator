
from PySide6 import QtWidgets
from PySide6.QtCore import Qt
import sys
import subprocess
import os
from pathlib import Path
import time
import math


test = 1
global_subprocess = 0
degree_setting_sincostan= 0 #0 = number, 1 = degrees

 
def isPi():
    return math.pi




def isSCT(problem): #Sin / Cos / Tan
    start_index = problem.find('(')
    end_index = problem.find(')')

    if "sin" in problem:
        clean_number = float(problem[start_index + 1 : end_index])
        if degree_setting_sincostan == 1:
            clean_number= math.radians(clean_number)
        return math.sin(clean_number)
    
    elif "cos" in problem:
        clean_number = float(problem[start_index + 1 : end_index])
        if degree_setting_sincostan == 1:
            clean_number= math.radians(clean_number)
        return math.cos(clean_number)
    
    elif "tan" in problem:
        clean_number = float(problem[start_index + 1 : end_index])
        if degree_setting_sincostan == 1:
            clean_number= math.radians(clean_number)
        return math.cos(clean_number)



    else:
        print("Error. Sin/Cos/tan wurde erkannt, aber konnte nicht zugeordnet werden.")


def isLog(number, base):
    ergebnis= None
    if base is None or base == 0:
        ergebnis = math.log(number)
    else:
        ergebnis = math.log(number, base)
    return ergebnis



def main():


    global global_subprocess
    global_subprocess = "0"
    ergebnis = "FEHLER: Keine Eingabe gefunden."

    
    if len(sys.argv) > 1 or test == 1:
        #received_string = sys.argv[1]
        received_string = "log(23)"
        global_subprocess = "1"
        start_index = received_string.find('(')
        end_index = received_string.find(')')

        if received_string == "π" or received_string.lower() == "pi":
            ergebnis = isPi()


        elif "sin" in received_string or "cos" in received_string or "tan" in received_string:
            ergebnis = isSCT(received_string)




        elif "log" in received_string:
            start_index = received_string.find('(')
            end_index = received_string.find(')')
            clean_number = received_string[start_index + 1: end_index]
            if "," in clean_number:
                eingabe_liste = clean_number.split(',', 1)
                number = float(eingabe_liste[0])
                base = float(eingabe_liste[1])
                ergebnis = isLog(number, base)
            else:
                ergebnis = isLog(float(clean_number), float(0))
        else:
            ergebnis = "Error. Konnte keine Operation zuordnen"
        print(ergebnis)
            


if __name__ == "__main__":
    main()
