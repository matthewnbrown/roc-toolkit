import copy
from datetime import datetime as dt, time
from typing import Callable
import os


class SettingsError(Exception):
    pass


def time_conv(t: str): return dt.strptime(t, '%H:%M').time() if len(
            t) <= 5 else dt.strptime(t, '%H:%M:%S').time()


class Setting:
    def __init__(self,
                 prettyname: str,
                 name: str,
                 default_value=None,
                 valtype: type = None,
                 description: str = None,
                 value=None,
                 validation_func: Callable = None) -> None:
        self.pname = prettyname
        self.name = name
        self.defaultval = default_value
        self.value = value if value else default_value
        self.valtype = valtype
        self.desc = description
        self.validation_func = validation_func

        if valtype and type(valtype) != type:
            print(f'Warning: {name} setting valtype is not a valid type.')
        elif value and valtype and type(self.value) != valtype:
            print(f'Warning: {name} setting type does not match value type.')


class Settings:
    DEFAULT_SETTINGS = {}

    def __init__(self, name: str = None, filepath=None) -> None:
        if not hasattr(self, 'settings'):
            self.settings = {}
            # self.settings = copy.deepcopy(Settings.DEFAULT_SETTINGS)
        if name is None:
            name = 'Settings'
        self.name = name
        self.mandatory = set()
        if filepath is not None:
            SettingsLoader.load_settings_from_path(
                filepath, settings=self.settings,
                default_settings=self.DEFAULT_SETTINGS, warnings=True)
            SettingsValidator.set_defaults_ifnotset(
                self.settings, self.DEFAULT_SETTINGS)

    def load_settings_from_path(self, filepath) -> None:
        SettingsLoader.load_settings_from_path(
            filepath, self.settings, warnings=True)
        SettingsValidator.check_mandatories(
            self.settings, self.mandatory, quit_if_bad=True)

    def get_setting(self, setting) -> Setting:
        if setting not in self.settings:
            return None
        return self.settings[setting]

    def set_setting(self, setting, value) -> None:
        self.settings[setting] = value

        if setting in self.mandatory:
            SettingsValidator.check_mandatories(
                self.settings, self.mandatory, quit_if_bad=True)

    def get_value(self, settingname: str):
        return self.settings[settingname].value

    def print_settings_and_values(self, enumerate: bool = False) -> None:
        print(self.name)
        i = 0
        for settingid, setting in self.settings.items():
            if enumerate:
                print('{}. '.format(i), end='')

            print('{} : {}'.format(settingid, setting))

    def print_settings(self, enumerate: bool = False) -> None:
        print(self.name)
        i = 0
        for setting, value in self.settings.items():
            if enumerate:
                print('{}. '.format(i), end='')

            print('{} : {}'.format(setting, value))

    def get_settings(self) -> dict[str, Setting]:
        return self.settings

    def get_settings_old(self) -> dict:
        res = {}
        for setting in self.settings:
            res[setting] = self.settings[setting].value
        return res


class SettingsConverter:
    def convert(value: str, valtype: type):
        if valtype in SettingsConverter.__convmap__:
            return SettingsConverter.__convmap__[valtype](value.strip())
        return value

    def __tostr__(value: str) -> str:
        return value

    def __toint__(value: str) -> int:
        return int(value.replace(',', '').replace(' ', ''))

    def __totime__(value: str) -> time:
        return time_conv(value)

    def __tofloat__(value: str) -> float:
        return float(value)

    def __tobool__(value: str) -> bool:
        value = value.lower()
        validans = ['yes', 'y', 'true', 'enable', 'enabled']
        return value in validans

    __convmap__ = {
        str: __tostr__,
        int: __toint__,
        time: __totime__,
        bool: __tobool__,
        float: __tofloat__,
        }


class SettingsLoader:
    def load_settings_from_path(filepath,
                                settings: dict[str, Setting],
                                default_settings: dict[str, Setting],
                                warnings: bool = False
                                ) -> dict:
        if settings is None:
            if warnings:
                print('Warning. Empty settings dict passed to loader')
            settings = {}

        with open(filepath) as f:
            lines = f.readlines()

        for line in lines:
            line = SettingsLoader.__split_comment(line)

            if ':' not in line and len(line.strip()) > 0:
                if warnings:
                    print(f'Warning: found non-setting line {line}')
                continue

            setting_name, value = line.split(':', maxsplit=1)
            setting_name = setting_name.strip()
            value = value.strip()
            if warnings and setting_name == '':
                print("Warning: A setting existed with no name")
                continue
            if warnings and len(value) == 0:
                print("Warning: setting {} has no value".format(setting_name))
                continue
            if setting_name not in default_settings:
                settings[setting_name] = Setting(
                    setting_name, setting_name)
                if warnings:
                    print(f"Warning: Setting {setting_name} found "
                          + "that is not in defaults")
            else:
                settings[setting_name] = copy.copy(
                    default_settings[setting_name])

            setting = settings[setting_name]
            try:
                setting.value = SettingsConverter.convert(
                    value, setting.valtype)
            except ValueError:
                raise SettingsError(
                    f'Error converting setting {setting.pname} with '
                    + f'value {value} to type {setting.valtype.__name__}')

        return settings

    def __split_comment(line: str) -> str:
        return line.split('#', maxsplit=1)[0]


class SettingsSaver:
    def __make_str(key, val) -> str:
        return '{}:{}\n'.format(key, val)

    def __make_lines(settings: dict):
        arr = []
        for key, val in settings.items():
            arr.append(SettingsSaver.__make_str(key, val.value))
        return arr

    def save_settings_toPath(filepath: str, settings: dict) -> None:
        lines = SettingsSaver.__make_lines(settings)

        with open(filepath, 'w') as f:
            f.writelines(lines)


class SettingsValidator:
    def __check_dict_generic(
            setdic: dict[str, Setting],
            key: str,
            default: Setting,
            callback: Callable
            ) -> None:
        if key not in setdic:
            print(f"Warning: setting {key} not in settings."
                  + f" Set to default value: {default.value}")
            setdic[key] = copy.copy(default)
        elif callback:
            setdic[key] = callback(setdic[key])

    def validate_set(settings: dict,
                     settings_to_validate,
                     validationfunc: Callable
                     ) -> bool:
        for item in settings_to_validate:
            if item not in settings or not validationfunc(settings[item]):
                return False
        return True

    def set_defaults_ifnotset(settings: dict[str, Setting],
                              defaults: dict[str, Setting],
                              callback: callable = None
                              ) -> None:
        if settings is None or defaults is None:
            return

        for key, val in defaults.items():
            SettingsValidator.__check_dict_generic(
                settings, key, val, callback)

    # Return true if all mandatories are set
    def check_mandatories(settings: dict[str, Setting],
                          mandatories,
                          printError: bool = True,
                          quit_if_bad=False
                          ) -> bool:
        if settings is None or mandatories is None:
            return False

        errorcount = 0
        for setting in mandatories:
            if setting not in settings\
                    or settings[setting] is None:
                if printError:
                    print("ERROR: {} setting not set!".format(setting))
                errorcount += 1

        if quit_if_bad and errorcount > 0:
            quit()

        return errorcount == 0

    def check_settings_in_range(
            settings: dict[str, Setting],
            warnings: bool = False) -> bool:

        valid = True
        for settingid, setting in settings.items():
            curvalid = True
            if setting.valtype:
                curvalid = type(setting.value) == setting.valtype
            if setting.validation_func:
                curvalid &= setting.validation_func(setting.value)

            if warnings and not curvalid:
                print(f'Warning: Settings {settingid} value is invalid')

            valid &= curvalid
        return valid


class SettingsSetupHelper:
    def needs_setup(path: str):
        return not os.path.isfile(path)

    def create_default_file(path: str, settings: Settings):
        SettingsSaver.save_settings_toPath(path, settings)
