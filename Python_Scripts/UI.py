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
        return "{}"




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


class Config_Signals(QObject):
    setting_changed = Signal(str, str)
    all_settings_loaded = Signal(dict)
    ergebnis = dict
    def __init__(self):
        super().__init__()
        pass


    def finished_first_loading(self, loaded_settings_dict: dict):
        self.all_settings_loaded.emit(loaded_settings_dict)

    def emit_setting_changed(self, key_value, new_value):
        self.all_settings_loaded.emit(key_value, new_value)

    def all_classes_ready(self):
        print("x")

class config_worker(QObject):
    job_finished = Signal(str)
    all_data = Signal(dict)

    use_degrees = False
    decimal_places = 2
    darkmode = True
    after_paste_enter = False

    def __init__(self, action, section, key_value, new_value):
        super().__init__()

        self.action = action
        self.section = section
        self.key_value = key_value
        self.new_value = new_value

    def load_all(self):
        global use_degrees, decimal_places, darkmode, after_paste_enter
        settings_dict = {}

        if first_run == True:
            ergebnis = Config_manager(self.action, self.section, self.key_value, self.new_value)
            settings_dict = json.loads(ergebnis)
            use_degrees = str(settings_dict['use_degrees'])
            decimal_places = int(settings_dict['decimal_places'])
            darkmode = str(settings_dict['darkmode'])
            after_paste_enter = str(settings_dict['after_paste_enter'])

            self.all_data.emit(settings_dict)
            global_config_signals.all_settings_loaded.emit(
                settings_dict)

        else:
            return settings_dict

    def load(self):
        if key_value == "use_degrees":
            return use_degrees
        elif key_value == "decimal_places":
            return decimal_places
        elif key_value == "darkmode":
            return darkmode
        elif key_value == "after_paste_enter":
            return after_paste_enter

    def save(self):
        global use_degrees, decimal_places, darkmode,after_paste_enter
        result_code = Config_manager(self.action, self.section, self.key_value, self.new_value)
        if result_code == "1":
            global_config_signals.setting_changed.emit(self.section, self.key_value)
        self.job_finished.emit(result_code)


class SettingsDialog(QtWidgets.QDialog):
    settings_saved = Signal()

    def __init__(self, parent=None):
        global previous_is_degree_active, previous_darkmode_active, previous_auto_enter_active, previous_input_text
        super().__init__(parent)
        self.load_worker = config_worker("load", "all", "", "")

        self.load_worker.all_data.connect(self.load_all_settings)

        self.load_thread = threading.Thread(target=self.load_worker.load_all)
        self.load_thread.start()
        previous_is_degree_active = ""
        previous_darkmode_active = ""
        previous_auto_enter_active = ""
        previous_input_text = ""


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
        #self.on_global_setting_update("darkmode", "True")



    def save_settings(self):
        global previous_is_degree_active, previous_darkmode_active, previous_auto_enter_active, previous_input_text
        is_degree_active = self.is_degree_mode_check.isChecked()
        darkmode_active = self.darkmode.isChecked()
        auto_enter_active = self.after_paste_enter.isChecked()
        input_text = self.input_field.text()

        input_decimals = input_text if input_text else "2"


        if str(is_degree_active) != str(previous_is_degree_active):
            worker_instanz = config_worker("save", "Scientific_Options", "use_degrees", str(is_degree_active))
            mein_thread = threading.Thread(target=worker_instanz.save)
            mein_thread.start()


        if str(darkmode_active) != str(previous_darkmode_active):
            worker_instanz = config_worker("save", "UI", "darkmode", str(darkmode_active))
            mein_thread = threading.Thread(target=worker_instanz.save)
            mein_thread.start()


        if str(auto_enter_active) != str(previous_auto_enter_active):
            worker_instanz = config_worker("save", "UI", "auto_enter_active", str(auto_enter_active))
            mein_thread = threading.Thread(target=worker_instanz.save)
            mein_thread.start()


        if str(input_text) != str(previous_input_text):
            worker_instanz = config_worker("save", "Math_Options", "decimal_places", str(input_text))
            mein_thread = threading.Thread(target=worker_instanz.save)
            mein_thread.start()


        erfolgreich_gespeichert = True


        if erfolgreich_gespeichert:
            self.settings_saved.emit()
            self.accept()
        else:
            QtWidgets.QMessageBox.critical(self, "Fehler", "Nicht alle Einstellungen konnten gespeichert werden.")
            self.reject()


        previous_is_degree_active = is_degree_active
        previous_darkmode_active = darkmode_active
        previous_auto_enter_active = auto_enter_active
        previous_input_text = input_text




    def on_global_setting_update(self, key_value, new_value):
        if key_value == "darkmode" and new_value == "True":
            self.setStyleSheet("""
                            QDialog {background-color: #121212;}
                            QLabel {color: white;}
                            QCheckBox {color: white;}
                            QLineEdit {background-color: #444444;color: white;border: 1px solid #666666;}
                            QDialogButtonBox QPushButton {background-color: #666666;color: white;}""")
        elif key_value == "darkmode" and new_value == "False":
            self.setStyleSheet("")



    def load_all_settings(self, settings_dict: dict):
        global previous_is_degree_active, previous_darkmode_active, previous_auto_enter_active, previous_input_text


        use_degrees = boolean(settings_dict['use_degrees'])
        decimal_places = int(settings_dict['decimal_places'])
        darkmode = boolean(settings_dict['darkmode'])
        after_paste_enter = boolean(settings_dict['after_paste_enter'])

        self.is_degree_mode_check.setChecked(use_degrees)
        self.darkmode.setChecked(darkmode)
        self.after_paste_enter.setChecked(after_paste_enter)
        self.input_field.setText(str(decimal_places))


        previous_is_degree_active = self.is_degree_mode_check.isChecked()
        previous_darkmode_active = self.darkmode.isChecked()
        previous_auto_enter_active = self.after_paste_enter.isChecked()
        previous_input_text = self.input_field.text()
        if darkmode == "True":
            self.setStyleSheet("""
                            QDialog {background-color: #121212;}
                            QLabel {color: white;}
                            QCheckBox {color: white;}
                            QLineEdit {background-color: #444444;color: white;border: 1px solid #666666;}
                            QDialogButtonBox QPushButton {background-color: #666666;color: white;}""")
        elif darkmode == False:
            self.setStyleSheet("")



class CalculatorPrototype(QtWidgets.QWidget):
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
                experiment = (button_instance.height()/8)*2
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
                    start_index = marker_index+1
                    temp_new_text = current_text[start_index:]
                    if temp_new_text.startswith(' '):
                        temp_new_text = temp_new_text[1:]
                    current_text = temp_new_text
                except ValueError:
                    pass

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

                response = Config_manager("load", "UI", "after_paste_enter", "0")

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
        global thread_active
        darkmode = Config_manager("load", "UI", "darkmode", "0") == "True"
        if darkmode == True:
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

        elif darkmode == False:
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


def starte_ladevorgang():
    global global_config_signals
    global_config_signals = Config_Signals()
    Config_Signals()
    SettingsDialog()
    CalculatorPrototype()
    print("--- MAIN: 'starte_ladevorgang' wurde aufgerufen.")
    worker = config_worker("load", "all", "...", "...")
    print("--- MAIN: Ladevorgang ist durch. 'emit' wurde gesendet.")



if __name__ == "__main__":
    side_thread = threading.Thread(target=starte_ladevorgang)
    side_thread.start()

    global_config_signals
    app = QtWidgets.QApplication(sys.argv)
    window = CalculatorPrototype()
    window.show()
    sys.exit(app.exec())
