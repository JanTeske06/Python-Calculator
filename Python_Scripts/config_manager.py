# config_manager.py
import sys
import configparser
from pathlib import Path
import json

config = Path(__file__).resolve().parent.parent / "config.ini"

def boolean(section, value):
    if value == "True":
        return True
    elif value == "False":
        return False
    else:
        return "-1"

def load_settings(section, key_value):
    cfg_instance = configparser.ConfigParser()
    cfg_instance.read(config, encoding='utf-8')


    if section == "all":
        config_data = {
            "use_degrees": cfg_instance.get("Scientific_Options", "use_degrees"),
            "decimal_places": cfg_instance.get("Math_Options", "decimal_places"),
            "darkmode": cfg_instance.get("UI", "darkmode"),
            "after_paste_enter": cfg_instance.get("UI", "after_paste_enter")
        }
        print(json.dumps(config_data))

    else:
        try:
            return_value = cfg_instance.get(str(section), str(key_value))
            print(return_value)
        except (configparser.NoSectionError, configparser.NoOptionError, ValueError):
            print("-1")


def save_settings(key_value, new_value):
    config_file = configparser.ConfigParser()
    config_file.read(config, encoding='utf-8')
    success = False

    if key_value == "decimal_places":
            if new_value != "":
                try:
                    val = int(new_value)
                    if val <= 2:
                        val = 2

                    config_file.set('Math_Options', 'decimal_places', str(val))
                    success = True
                except:
                    config_file.set('Math_Options', 'decimal_places', str(2))
                    success = False
            else:
                success = False

    elif key_value == "darkmode" or key_value == "after_paste_enter":
            if new_value in ("True", "False"):
                config_file.set('UI', key_value, str(new_value))
                success = True
            else:
                success = False


    elif key_value == "use_degrees":
            if new_value in ("True", "False"):
                config_file.set('Scientific_Options', 'use_degrees', str(new_value))
                success = True
            else:
                success = False
    else:
        success = False

    if success:
        try:
            with open(config, 'w', encoding='utf-8') as configfile:
                config_file.write(configfile)
            print("1")
        except Exception as e:
            print(f"FEHLER: Konnte {config} nicht speichern: {e}")

    else:
        print("-1")


def main():
    test = 0
    if len(sys.argv) < 5 and test == 0:
        print("Fehler. Es wurden nicht genügend Argumente übergeben.")
        sys.exit(1)
    else:
        #
        befehl = sys.argv[1]
        section = sys.argv[2]
        key_value = sys.argv[3]
        new_value = sys.argv[4]
        # befehl = "save"
        # section = "UI"
        # key_value = "darkmode"
        # new_value = "False"

    if befehl == "save":
        save_settings(str(key_value), str(new_value))

    elif befehl == "load":
        load_settings(section, key_value)

    else:
        print("Fehler. Es wurde kein gültiger Befehl übergeben.")
        sys.exit(1)


if __name__ == "__main__":

    main()
