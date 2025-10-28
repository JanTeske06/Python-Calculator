#ScientificEngine
from PySide6 import QtWidgets
from PySide6.QtCore import Qt
import sys
import subprocess
import os
from pathlib import Path
import time
import math
import configparser

config = Path(__file__).resolve().parent / "config.ini"


test = 1
global_subprocess = 0


degree_setting_sincostan= 0 #0 = number, 1 = degrees


def settings_load():
    global degree_setting_sincostan
    cfg_objekt = configparser.ConfigParser()
    cfg_objekt.read(config, encoding='utf-8')


    try:
        ist_aktiv = cfg_objekt.getboolean('Scientific_Options', 'use_degrees')
        if ist_aktiv == True:
            degree_setting_sincostan = 1

        elif ist_aktiv == False:
            degree_setting_sincostan = 0


    except (configparser.NoSectionError, configparser.NoOptionError, ValueError):
        degree_setting_sincostan = 0
        print(f"Wanrung: Konnte nicht die IWnkeleinstellung aus config.ini auslesen. Fehler: {e}")



 
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
        return math.tan(clean_number)



    else:
        print("Error. Sin/Cos/tan wurde erkannt, aber konnte nicht zugeordnet werden.")


def isLog(problem):
    start_index = problem.find('(')
    end_index = problem.find(')')
    if start_index == -1 or end_index == -1 or start_index >= end_index:
        return "FEHLER: Logarithmus-Syntax."

    content = problem[start_index + 1: end_index]

    number = 0.0
    base = 0.0
    ergebnis = "FEHLER: Unbekannter Logarithmusfehler."

    try:
        if "," in content:
            number_str, base_str = content.split(',', 1)
            number = float(number_str.strip())
            base = float(base_str.strip())
        else:
            number = float(content.strip())
            base = 0.0

        if base == 0.0:
            ergebnis = math.log(number)
        else:
            ergebnis = math.log(number, base)

    except ValueError:
        return "FEHLER: Ungültige Zahl oder Basis im Logarithmus."
    except Exception as e:
        return f"FEHLER: Logarithmus-Berechnung: {e}"

    return ergebnis


def isE(problem):
    start_index = problem.find('(')
    end_index = problem.find(')')
    clean_number = problem[start_index + 1: end_index]
    ergebnis = math.exp(float(clean_number))
    return ergebnis



def isRoot(problem):
    start_index = problem.find('(')
    end_index = problem.find(')')
    clean_number = problem[start_index + 1: end_index]
    ergebnis = math.sqrt(float(clean_number))
    return ergebnis


def main():
    global global_subprocess
    global_subprocess = "0"
    ergebnis = "FEHLER: Keine Eingabe gefunden."

    
    if len(sys.argv) > 1 or test == 1:
        received_string = sys.argv[1]
        #received_string = "e^(3)"
        global_subprocess = "1"
        start_index = received_string.find('(')
        end_index = received_string.find(')')

        if received_string == "π" or received_string.lower() == "pi":
            ergebnis = isPi()


        elif "sin" in received_string or "cos" in received_string or "tan" in received_string:
            ergebnis = isSCT(received_string)

        elif "log" in received_string:
            ergebnis = isLog(received_string)

        elif "√" in received_string:
            ergebnis = isRoot(received_string)

        elif "e" in received_string:
            ergebnis = isE(received_string)


        else:
            ergebnis = (f"Error. Konnte keine Operation zuordnen. Received String:" + str(received_string))
        print(ergebnis)
            


if __name__ == "__main__":
    settings_load()
    main()
