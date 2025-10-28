#Ui.py
from PySide6 import QtWidgets, QtGui
from PySide6.QtCore import Qt
import sys
import subprocess
import os
from pathlib import Path
import time
import configparser
import threading
from PySide6.QtCore import QObject, Signal, QTimer


config = Path(__file__).resolve().parent / "config.ini"
MathEngine = str(Path(__file__).resolve().parent / "MathEngine.py")
python_interpreter = sys.executable

undo = ["0"]
redo = []
buttons = []
expanding_policy = ""
first_run = True
thread_active = False
darkmode = False


def Calc(problem):
    cmd = [
        python_interpreter,
        MathEngine,
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


def background_process(current_text):
    return Calc(current_text)


class Worker(QObject):
    job_finished = Signal(str, str)
    global thread_active
    def __init__ (self,problem):
        super().__init__()
        self.daten = problem
        self.previous = problem
    def run_Calc(self):
        global thread_active
        ergebnis = Calc(self.daten)
        self.job_finished.emit(ergebnis, self.previous)
        thread_active = False


class SettingsDialog(QtWidgets.QDialog):
    settings_saved = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Calculator Settings")
        self.resize(300, 200)
        self.setMinimumSize(300, 200)
        self.setMaximumSize(300, 200)


        main_layout = QtWidgets.QVBoxLayout(self)

        row_h_layout = QtWidgets.QHBoxLayout()
        main_layout.addLayout(row_h_layout)
        label = QtWidgets.QLabel("Decimal places (min. 2):")
        self.input_field = QtWidgets.QLineEdit()

        row_h_layout.addWidget(label)
        row_h_layout.addWidget(self.input_field)
        row_h_layout.setStretch(1, 1)

        self.is_degree_mode_check = QtWidgets.QCheckBox("Winkel in Grad (°)")
        main_layout.addWidget(self.is_degree_mode_check)

        self.darkmode = QtWidgets.QCheckBox("Darkmode")
        main_layout.addWidget(self.darkmode)


        button_box = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel)
        main_layout.addWidget(button_box)
        main_layout.addStretch(1)

        button_box.accepted.connect(self.save_settings)

        button_box.rejected.connect(self.reject)
        self.load_current_settings()
        self.update_darkmode()



    # 2e2e2e
    #121212

    def save_settings(self):
        is_degree_active = self.is_degree_mode_check.isChecked()
        darkmode_active = self.darkmode.isChecked()

        config_file = configparser.ConfigParser()
        config_file.read(config, encoding='utf-8')

        input_text = self.input_field.text()
        input = 2
        if input_text != "":
            try:
                input = int(input_text)
                if input <= 2:
                    input = 2

            except:
                input = 2


        if config_file.get('Math_Options', 'decimal_places') != str(input):
            config_file.set('Math_Options', 'decimal_places', str(input))



        if is_degree_active:
            config_file.set('Scientific_Options', 'use_degrees', 'True')
        else:
            config_file.set('Scientific_Options', 'use_degrees', 'False')

        if darkmode_active:
            config_file.set('UI', 'darkmode', 'True')
        else:
            config_file.set('UI', 'darkmode', 'False')


        try:
            with open(config, 'w', encoding='utf-8') as configfile:
                config_file.write(configfile)
            self.settings_saved.emit()
            self.accept()

        except Exception as e:
            print(f"FEHLER beim Speichern: {e}")
            self.reject()

    def update_darkmode(self):
        if darkmode_active:
            self.setStyleSheet("""
                        QDialog {background-color: #121212;}
                        QLabel {color: white;}
                        QCheckBox {color: white;}
                        QLineEdit {background-color: #444444;color: white;border: 1px solid #666666;}
                        QDialogButtonBox QPushButton {background-color: #666666;color: white;}""")
        else:
            self.setStyleSheet("")

    def load_current_settings(self):
        global darkmode_active
        cfg = configparser.ConfigParser()
        cfg.read(config, encoding='utf-8')

        try:
            is_active = cfg.getboolean('Scientific_Options', 'use_degrees')
            self.is_degree_mode_check.setChecked(is_active)
        except (configparser.NoSectionError, configparser.NoOptionError, ValueError):
            self.is_degree_mode_check.setChecked(False)

        try:
            decimals = cfg.get('Math_Options', 'decimal_places', fallback='2')
            self.input_field.setPlaceholderText(decimals)

        except (configparser.NoSectionError, configparser.NoOptionError):
            self.input_field.setText('2')

        try:
            darkmode_active = cfg.getboolean('UI', 'darkmode', fallback='False')
            self.darkmode.setChecked(darkmode_active)

        except (configparser.NoSectionError, configparser.NoOptionError):
            self.darkmode.setChecked(False)



class CalculatorPrototype(QtWidgets.QWidget):
    def __init__(self):

        global darkmode_active
        global buttons
        global expanding_policy
        global first_run
        super().__init__()
        icon = QtGui.QIcon(str(Path(__file__).resolve().parent / "icon.png"))
        self.setWindowIcon(icon)
        self.button_objects = {}
        self.setWindowTitle("Calculator")
        self.resize(200, 450)

        main_v_layout = QtWidgets.QVBoxLayout(self)

        expanding_policy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Policy.Expanding,
            QtWidgets.QSizePolicy.Policy.Expanding
        )
        # Display (Stretch 1)
        self.display = QtWidgets.QLineEdit("0")
        self.display.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.display.setReadOnly(True)
        font = self.display.font()
        font.setPointSize(46)
        self.display.setFont(font)

        self.display.setSizePolicy(expanding_policy)
        main_v_layout.addWidget(self.display, 1)


        button_container = QtWidgets.QWidget()
        main_v_layout.addWidget(button_container, 4)

        button_grid = QtWidgets.QGridLayout(button_container)

        button_grid.setSpacing(0)
        button_grid.setContentsMargins(0, 0, 0, 0)

        for i in range(7):  # vertikal
            button_grid.setRowStretch(i, 1)
        for j in range(5):  # horizental
            button_grid.setColumnStretch(j, 1)
        cfg = configparser.ConfigParser()
        cfg.read(config, encoding='utf-8')

        try:
            darkmode_active = cfg.getboolean('UI', 'darkmode', fallback=False)
            if darkmode_active == True:
                print("X")
        except (configparser.NoSectionError, configparser.NoOptionError):
            darkmode_active = False

        buttons = [
            ('⚙️', 0, 0), ('📋', 0, 1), ('↷', 0, 2), ('↶', 0, 3), ('<', 0, 4),

            ('π', 1, 0), ('e^(', 1, 1), ('x', 1, 2), ('√(', 1, 3), ('/', 1, 4),

            ('sin(', 2, 0), ('(', 2, 1), (')', 2, 2), ('^(', 2, 3), ('*', 2, 4),

            ('cos(', 3, 0),  ('7', 3, 1), ('8', 3, 2), ('9', 3, 3), ('-', 3, 4),

            ('tan(', 4, 0), ('4', 4, 1), ('5', 4, 2), ('6', 4, 3), ('+', 4, 4),

            ('log(', 5, 0), ('1', 5, 1), ('2', 5, 2), ('3', 5, 3), ('=', 5, 4),

            ('C', 6, 0), (',', 6, 1), ('0', 6, 2), ('.', 6, 3), ('⏎', 6, 4)
        ]
        for text, row, col in buttons:
            button = QtWidgets.QPushButton(text)
            button.setSizePolicy(expanding_policy)

            if text == '⏎':
                # Das Stylesheet setzt die Farbe
                button.setStyleSheet("background-color: #007bff; color: white; font-weight: bold;")


            elif text == '⚙️':
                button.clicked.connect(self.open_settings)


            button.clicked.connect(lambda checked=False, val=text: self.handle_button_press(val))
            button_grid.addWidget(button, row, col)
            self.button_objects[text] = button
            self.update_darkmode()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.setMinimumSize(400, 540)
        global  first_run
        if first_run == False:
            for button_text, button_instance in self.button_objects.items():
                experiment = (button_instance.height()/10)*2
                if experiment <= 12:
                    experiment = 12
                font = button_instance.font()
                font.setPointSize((experiment))
                button_instance.setFont(font)
        elif first_run == True:
            for button_text, button_instance in self.button_objects.items():
                font = button_instance.font()
                font.setPointSize((12))
                button_instance.setFont(font)
                first_run  = False

    def handle_button_press(self, value):
        global undo
        global redo
        global first_run
        global mein_thread

        current_text = self.display.text()

        if value == 'C':
            self.display.setText("0")
            return

        elif (value == '<'):
            if len(current_text) <= 1 or current_text == "0":
                self.display.setText("0")
                return
            new_text = current_text[:-1]
            self.display.setText(new_text)
            return

        elif (value == '⚙️'):
            return

        elif value == '⏎':
            global thread_active

            if thread_active:
                print("FEHLER: Eine Berechnung läuft bereits!")
                return
            else:
                thread_active = True
                self.update_return_button()


            self.display.setText("...")
            return_button = self.button_objects['⏎']
            QtWidgets.QApplication.processEvents()
            worker_instanz = Worker(current_text)
            mein_thread = threading.Thread(target=worker_instanz.run_Calc)
            mein_thread.start()
            worker_instanz.job_finished.connect(self.Calc_result)
            return

        elif value == '↶':
            if len(undo) > 1:
                redo.append(undo.pop())
                current_text = undo[-1]
                self.display.setText(current_text)
                print(f"Es wurde die Taste '{value}' gedrückt.")
            return

        elif value == '📋':
            clipboard = QtWidgets.QApplication.clipboard()
            clipboard_text = clipboard.text()
            current_text = self.display.text()
            if clipboard_text:
                if current_text == "0":
                    new_text = clipboard_text
                else:
                    new_text = current_text + clipboard_text
                self.display.setText(new_text)
                undo.append(new_text)
                redo.clear()
            return



        elif value == '↷':
            if len(redo) > 0:
                undo.append(redo.pop())
                current_text = undo[-1]
                self.display.setText(current_text)
                print(f"Es wurde die Taste '{value}' gedrückt.")
            return


        else:
            if current_text == "0":
                current_text = ""
            current_text += str(value)

        self.display.setText(current_text)

        undo.append(current_text)
        redo.clear()


        print(f"Es wurde die Taste '{value}' gedrückt.")


    def update_return_button(self):
        global thread_active
        return_button = self.button_objects.get('⏎')
        if not return_button:
            return
        if thread_active == True:
            return_button.setStyleSheet("background-color: #FF0000; color: white; font-weight: bold;")
            return_button.setText("X")
        elif thread_active == False:
            return_button.setStyleSheet("background-color: #007bff; color: white; font-weight: bold;")
            return_button.setText("⏎")
        return_button.update()

    def update_darkmode(self):
        global  darkmode
        cfg = configparser.ConfigParser()
        cfg.read(config, encoding='utf-8')

        try:
            darkmode = cfg.getboolean('UI', 'darkmode', fallback='False')

        except (configparser.NoSectionError, configparser.NoOptionError):
            darkmode = False

        if darkmode == True:
            for text, button in self.button_objects.items():
                if text != '⏎':
                    button.setStyleSheet("background-color: #121212; color: white; font-weight: bold;")
                    button.update()
            self.setStyleSheet(f"background-color: #121212;")
            self.display.setStyleSheet("background-color: #121212; color: white; font-weight: bold;")

        elif darkmode == False:
            for text, button in self.button_objects.items():
                button.setStyleSheet("")
                button.update()
            self.setStyleSheet("")
            self.display.setStyleSheet("")

    def open_settings(self):
        settings_dialog = SettingsDialog(self)
        settings_dialog.exec()
        self.update_darkmode()


    def Calc_result(self, ergebnis, current_text):
        self.update_return_button()
        if ergebnis == "True":
            current_text = (ergebnis + "    " + current_text)
            print(f"Ergebnis: {ergebnis}")
        elif ergebnis == "False":
            current_text = (ergebnis + "    " + current_text)
            print(f"Ergebnis: {ergebnis}")
        else:
            current_text = ergebnis

        self.display.setText(current_text)

        undo.append(current_text)
        redo.clear()

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = CalculatorPrototype()
    window.show()
    sys.exit(app.exec())
