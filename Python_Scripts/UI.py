# Ui.py
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
import json

received_result = False

config = Path(__file__).resolve().parent.parent / "config.ini"
config_man = str(Path(__file__).resolve().parent / "config_manager.py")
MathEngine = str(Path(__file__).resolve().parent / "MathEngine.py")
python_interpreter = sys.executable

undo = ["0"]
redo = []
buttons = []
expanding_policy = ""
first_run = True
thread_active = False
darkmode = False

def boolean(value):
    if value == "True":
        return True
    elif value == "False":
        return False
    else:
        return "-1"

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
            encoding='utf-8',
            check=True)
        zurueckgeschickter_string = ergebnis.stdout.strip()
        zurueckgeschickter_string = ergebnis.stdout.strip()
        return zurueckgeschickter_string
    except subprocess.CalledProcessError as e:
        print(f"Ein Fehler ist aufgetreten: {e}")


def Config_manager(action, section, key_value, new_value):
    cmd = [
        python_interpreter,
        config_man,
        action,
        section,
        key_value,
        new_value
    ]
    try:
        ergebnis = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            encoding='utf-8',
            check=True)
        zurueckgeschickter_string = ergebnis.stdout.strip()
        zurueckgeschickter_string = ergebnis.stdout.strip()
        return zurueckgeschickter_string
    except subprocess.CalledProcessError as e:
        print(f"Ein Fehler ist aufgetreten: {e}")


def background_process(current_text):
    return Calc(current_text)


class Worker(QObject):
    job_finished = Signal(str, str)
    global thread_active

    def __init__(self, problem):
        super().__init__()
        self.daten = problem
        self.previous = problem

    def run_Calc(self):
        global thread_active
        ergebnis = Calc(self.daten)
        self.job_finished.emit(ergebnis, self.previous)
        thread_active = False



class Config_Signal(QObject):
    all_settings = dict
    def __init__(self):
        global all_settings
        super().__init__()
        all_settings = json.loads(Config_manager("load", "all", "0", "0"))
        print(all_settings)
    def load(self, key_value):
        return all_settings[str(key_value)]
    def save(self, section, key_value, new_value):
        return (Config_manager("save", str(section), str(key_value), str(new_value)))



class SettingsDialog(QtWidgets.QDialog):
    settings_saved = Signal()
    config_handler = Config_Signal()

    def __init__(self, parent=None):
        super().__init__(parent)

        self.previous_is_degree_active = "False"
        self.previous_darkmode_active = "False"
        self.previous_auto_enter_active = "False"
        self.previous_input_text = "2"

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

        self.after_paste_enter = QtWidgets.QCheckBox("Nach 📋 automatisch Enter")
        main_layout.addWidget(self.after_paste_enter)

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
    # 121212
    def load_current_settings(self):

        def get_setting(key_value):
            response = self.config_handler.load(key_value)

            if response == "-1":
                return None
            return response

        decimals_str = get_setting("decimal_places")
        if decimals_str is not None:
            self.input_field.setPlaceholderText(decimals_str)
        else:
            self.input_field.setPlaceholderText('2')

        is_degree_active_str = get_setting("use_degrees")


        if str(is_degree_active_str) == "True":
            self.is_degree_mode_check.setChecked(True)
        else:
            self.is_degree_mode_check.setChecked(False)


        after_paste_enter_str = get_setting("after_paste_enter")
        if str(after_paste_enter_str) == "True":
            self.after_paste_enter.setChecked(True)
        else:
            self.after_paste_enter.setChecked(False)
        darkmode_active_str = get_setting("darkmode")
        if str(darkmode_active_str) == "True":
            self.darkmode.setChecked(True)
        elif str(darkmode_active_str) == "False":
            self.darkmode.setChecked(False)

        self.previous_is_degree_active = is_degree_active_str if is_degree_active_str is not None else "False"
        self.previous_darkmode_active = darkmode_active_str if darkmode_active_str is not None else "False"
        self.previous_auto_enter_active = after_paste_enter_str if after_paste_enter_str is not None else "False"
        self.previous_input_text = decimals_str if decimals_str is not None else "2"





    def save_settings(self):

        is_degree_active = str(self.is_degree_mode_check.isChecked())
        darkmode_active = str(self.darkmode.isChecked())
        auto_enter_active = str(self.after_paste_enter.isChecked())

        input_text = self.input_field.text()
        input_decimals = input_text if input_text else "2"
        default_decimals = self.input_field.placeholderText() if self.input_field.placeholderText() else "2"
        input_decimals = input_text if input_text else default_decimals
        erfolgreich_gespeichert = True

        response = ""
        error_message = ""

        if (is_degree_active != self.previous_is_degree_active):
            response = self.config_handler.save("Scientific_Options", "use_degrees", str(is_degree_active))
            if response != "1" and not response == "":
                erfolgreich_gespeichert = False
                print("Fehler beim speichern")
                error_message = error_message + " / Degree mode"
            elif response == "1":
                self.previous_is_degree_active = is_degree_active

        if darkmode_active != self.previous_darkmode_active:
            response = self.config_handler.save("UI","darkmode", str(darkmode_active))
            if response != "1" and not response == "":
                erfolgreich_gespeichert = False
                print("Fehler beim speichern")
                error_message = error_message + " / Darkmode"
            elif response == "1":
                self.previous_darkmode_active = darkmode_active


        if auto_enter_active != self.previous_auto_enter_active:
            response = self.config_handler.save("UI","after_paste_enter", str(auto_enter_active))
            if response != "1" and not response == "":
                erfolgreich_gespeichert = False
                print("Fehler beim speichern")
                error_message = error_message + " / Enter after Paste"
            elif response == "1":
                self.previous_auto_enter_active = auto_enter_active

        if input_decimals != self.previous_input_text:
            response = self.config_handler.save("Math_Options", "decimal_places", str(input_decimals))

            if response != "1" and not response == "":
                erfolgreich_gespeichert = False
                error_message = error_message + " / Decimals"
            elif response == "1":
                self.previous_input_text = input_decimals


        if erfolgreich_gespeichert or response == "":
            self.settings_saved.emit()
            self.accept()
            Config_Signal()
            self.load_current_settings()
        else:
            QtWidgets.QMessageBox.critical(self, "Fehler", "Nicht alle Einstellungen konnten gespeichert werden." + error_message)





    def update_darkmode(self):
        if self.config_handler.load("darkmode") == "True":
            self.setStyleSheet("""
                        QDialog {background-color: #121212;}
                        QLabel {color: white;}
                        QCheckBox {color: white;}
                        QLineEdit {background-color: #444444;color: white;border: 1px solid #666666;}
                        QDialogButtonBox QPushButton {background-color: #666666;color: white;}""")
        else:
            self.setStyleSheet("")


class CalculatorPrototype(QtWidgets.QWidget):
    config_handler = Config_Signal()
    display_font_size = 4.8
    def __init__(self):

        global darkmode_active
        global buttons
        global expanding_policy
        global first_run
        super().__init__()


        icon_path = Path(__file__).resolve().parent.parent / "icons" / "icon.png"
        app_icon = QtGui.QIcon(str(icon_path))



        self.setWindowIcon(app_icon)

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

        buttons = [
            ('⚙️', 0, 0), ('📋', 0, 1), ('↷', 0, 2), ('↶', 0, 3), ('<', 0, 4),

            ('π', 1, 0), ('e^(', 1, 1), ('x', 1, 2), ('√(', 1, 3), ('/', 1, 4),

            ('sin(', 2, 0), ('(', 2, 1), (')', 2, 2), ('^(', 2, 3), ('*', 2, 4),

            ('cos(', 3, 0), ('7', 3, 1), ('8', 3, 2), ('9', 3, 3), ('-', 3, 4),

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
        global first_run
        if first_run == False:
            for button_text, button_instance in self.button_objects.items():
                experiment = (button_instance.height() / 8) * 2
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
                first_run = False
        self.update_font_size_display()

    def handle_button_press(self, value):
        global undo
        global redo
        global first_run
        global mein_thread
        global received_result

        current_text = self.display.text()

        if received_result == True:
            received_result = False
            ungefaehr_zeichen = "\u2248"
            marker_to_find = ""

            if "=" in current_text:
                marker_to_find = "="
            elif ungefaehr_zeichen in current_text:
                marker_to_find = ungefaehr_zeichen

            if marker_to_find != "":
                try:
                    marker_index = current_text.index(marker_to_find)
                    start_index = marker_index + 1
                    temp_new_text = current_text[start_index:]
                    if temp_new_text.startswith(' '):
                        temp_new_text = temp_new_text[1:]
                    current_text = temp_new_text
                except ValueError:
                    pass

        if value == 'C':
            current_text = "0"
            self.display.setText(current_text)

        elif (value == '<'):
            if len(current_text) <= 1 or current_text == "0":
                current_text = "0"
                self.display.setText(current_text)
                return
            current_text = current_text[:-1]
            self.display.setText(current_text)

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

                response = self.config_handler.load("after_paste_enter")

                if response == "False":
                    pass
                elif response == "True":
                    if thread_active:
                        print("FEHLER: Eine Berechnung läuft bereits!")
                        return
                    else:
                        thread_active = True
                        self.update_return_button()
                        self.display.setText("...")
                        worker_instanz = Worker(clipboard_text)

                        mein_thread = threading.Thread(target=worker_instanz.run_Calc)
                        mein_thread.start()
                        worker_instanz.job_finished.connect(self.Calc_result)

            return


        elif value == '↷':
            if len(redo) > 0:
                undo.append(redo.pop())
                current_text = undo[-1]
                self.display.setText(current_text)
                print(f"Es wurde die Taste '{value}' gedrückt.")


        else:
            if current_text == "0":
                current_text = ""
            current_text += str(value)
            self.display.setText(current_text)

        self.update_font_size_display()


        if value != '↶' and value != '↷' and value != '📋':
            undo.append(current_text)
            redo.clear()

        print(f"Es wurde die Taste '{value}' gedrückt.")

    def update_font_size_display(self):
            current_text = self.display.text()
            MAX_FONT_SIZE = 46
            MIN_FONT_SIZE = 10

            self.display.setText(current_text)

            font = self.display.font()
            aktuelle_groesse = font.pointSize()
            fm = QtGui.QFontMetrics(font)

            r_margin = self.display.textMargins().right()
            l_margin = self.display.textMargins().left()
            padding = l_margin + r_margin + 5
            verfuegbare_breite = self.display.width() - padding

            text_breite = fm.horizontalAdvance(current_text)

            while text_breite > verfuegbare_breite and aktuelle_groesse > MIN_FONT_SIZE:
                aktuelle_groesse -= 1
                font.setPointSize(aktuelle_groesse)
                fm = QtGui.QFontMetrics(font)
                text_breite = fm.horizontalAdvance(current_text)

            temp_size = aktuelle_groesse

            while temp_size < MAX_FONT_SIZE:
                temp_size += 1
                font.setPointSize(temp_size)
                fm_temp = QtGui.QFontMetrics(font)
                text_breite_temp = fm_temp.horizontalAdvance(current_text)
                if text_breite_temp <= verfuegbare_breite:
                    aktuelle_groesse = temp_size
                else:
                    temp_size -= 1
                    break
            font.setPointSize(aktuelle_groesse)
            self.display.setFont(font)


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
        global darkmode
        global thread_active

        if self.config_handler.load("darkmode") == "True":
            for text, button in self.button_objects.items():
                if text != '⏎':
                    button.setStyleSheet("background-color: #121212; color: white; font-weight: bold;")
                    button.update()
                if text == '⏎':
                    return_button = self.button_objects.get('⏎')
                    if not return_button:
                        return
                    if thread_active == True:
                        return_button.setStyleSheet("background-color: #FF0000; color: white; font-weight: bold;")
                        return_button.setText("X")
                    elif thread_active == False:
                        return_button.setStyleSheet("background-color: #007bff; color: white; font-weight: bold;")
                        return_button.setText("⏎")

            self.setStyleSheet(f"background-color: #121212;")
            self.display.setStyleSheet("background-color: #121212; color: white; font-weight: bold;")

        elif self.config_handler.load("darkmode") == "False":
            for text, button in self.button_objects.items():
                if text != '⏎':
                    button.setStyleSheet("font-weight: normal;")
                    button.update()
                if text == '⏎':
                    return_button = self.button_objects.get('⏎')
                    if not return_button:
                        return
                    if thread_active == True:
                        return_button.setStyleSheet("background-color: #FF0000; color: white; font-weight: bold;")
                        return_button.setText("X")
                    elif thread_active == False:
                        return_button.setStyleSheet("background-color: #007bff; color: white; font-weight: bold;")
                        return_button.setText("⏎")
            self.setStyleSheet("")
            self.display.setStyleSheet("")

    def open_settings(self):
        settings_dialog = SettingsDialog(self)
        settings_dialog.exec()
        self.update_darkmode()

    def Calc_result(self, ergebnis, current_text):
        global received_result
        received_result = True
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
    Config_Signal()
    app = QtWidgets.QApplication(sys.argv)
    window = CalculatorPrototype()
    window.show()
    sys.exit(app.exec())
