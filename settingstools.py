from datetime import datetime
from typing import Callable
from urllib.parse import urlparse

class Settings:
    def __init__(self, name: str = None, filepath = None) -> None:
        self.settings = {}
        if name is None:
            name = 'Settings'
        self.name = name
        self.mandatory = set()
        if filepath is not None:
            SettingsLoader.load_settings_from_path(filepath, settings=self.settings, warnings=True)         

    def load_settings_from_path(self, filepath) -> None:
        SettingsLoader.load_settings_from_path(filepath, self.settings, warnings=True)
        SettingsValidator.check_mandatories(self.settings, self.mandatory, quit_if_bad=True)

    def get_setting(self, setting) -> None:
        if setting not in self.settings:
            return None
        return self.settings[setting]
    
    def set_setting(self, setting, value) -> None:
        self[setting] = value
        
        if setting in self.mandatory:
            SettingsValidator.check_mandatories(self.settings, self.mandatory, quit_if_bad=True)

    def print_settings_and_values(self, enumerate: bool = False) -> None:
        print(self.name)
        i = 0
        for setting, value in self.settings.items():
            if enumerate:
                print('{}. '.format(i), end='');

            print('{} : {}'.format(setting, value))
    
    def print_settings(self, enumerate: bool = False) -> None:
        print(self.name)
        i = 0
        for setting, value in self.settings.items():
            if enumerate:
                print('{}. '.format(i), end='');

            print('{} : {}'.format(setting, value))

    def get_settings(self):
        return self.settings

class UserSettings(Settings):
    def __init__(self, name: str = None, filepath=None) -> None:
        if name is None:
            name = 'User Settings'
        super().__init__(name, filepath)

        self.mandatory = {'email', 'password'}

        if(filepath is not None):
            self.__check_valid_settings()

    def load_settings_from_path(self, filepath) -> None:
        super().load_settings_from_path(filepath)
        self.__check_valid_settings()

    def __check_valid_settings(self):
        default_bools = { 'auto_solve_captchas':False, 'enable_nightmode': False }
        default_ints = {'notify_soldier_amt':60, 'min_checktime_secs':300, 'max_checktime_secs':600,
        'nightmode_minwait_mins': 60, 'nightmode_maxwait_mins':120 }

        timeConv = lambda t : datetime.strptime(t, '%H:%M').time()

        default_shorttime = {'nightmode_begin': timeConv('00:00'), 'nightmode_end': timeConv('9:00') }

        SettingsValidator.check_mandatories(self.settings, self.mandatory, quit_if_bad=True)
        SettingsValidator.set_defaults_ifnotset(self.settings, default_bools, lambda s : s.lower() == 'true')
        SettingsValidator.set_defaults_ifnotset(self.settings, default_ints, lambda i : int(i))
        SettingsValidator.set_defaults_ifnotset(self.settings, default_shorttime, timeConv)


class SiteSettings(Settings):
    def __init__(self, name: str = None, filepath=None) -> None:
        if name is None:
            name = 'Site Settings'
        super().__init__(name, filepath)

        self.mandatory = {'roc_home', 'roc_home', 'roc_home'}
 
        if filepath is not None:
            SettingsValidator.check_mandatories(self.settings, self.mandatory, quit_if_bad=True)
            validUrls = SettingsValidator.validate_set(self.settings, self.mandatory, SiteSettings.__url_valid)

            if not validUrls:
                print("Site settings are not set correctly. Ensure URLs are valid. Exiting");
                quit()
        
    def __url_valid(urlstr: str) -> bool:
        try:
            result = urlparse(urlstr)
            return all([result.scheme, result.netloc])
        except ValueError:
            return False

class SettingsLoader:
    def __init__(self) -> None:
        pass

    def load_settings_from_path(filepath, settings: dict = None, warnings: bool = False) -> dict:
        if settings is None:
            settings = {}
        
        with open(filepath) as f:
            lines = f.readlines()

        for line in lines:
            setting_name, value = line.split(':',maxsplit=1)
            setting_name = setting_name.strip()
            value = value.strip()
            if warnings and setting_name == '':
                print("Warning: A setting existed with no value")
                continue
            if warnings and len(value) == 0:
                print("Warning: setting {} has no value".format(setting_name))
                continue
            settings[setting_name] = value

class SettingsValidator:
    def __init__(self) -> None:
        pass

    def __check_dict_generic(setdic, key, default, callback: Callable) -> None:
        if key not in setdic:
            setdic[key] = default
        else:
            setdic[key] = callback(setdic[key])

    def validate_set(settings: dict, settings_to_validate, validationfunc: Callable) -> bool:
        for setting in settings_to_validate:
            if setting not in settings or not validationfunc(settings[setting]):
                return False
        return True

    def set_defaults_ifnotset(settings: dict, defaults: dict, callback: callable) -> None:
        if settings is None or defaults is None or callback is None:
            return
        
        for key, val in defaults.items():
            SettingsValidator.__check_dict_generic(settings, key, val, callback)

    # Return true if all mandatories are set
    def check_mandatories(settings: dict, mandatories, printError: bool = True, quit_if_bad = False) -> bool:
        if settings is None or mandatories is None:
            return False

        errorcount = 0
        for setting in mandatories:
            if setting not in settings or settings[setting] is None or len(settings[setting]) == 0:
                if printError:
                    print("ERROR: {} setting not set!".format(setting))
                errorcount += 1
        
        if quit_if_bad and errorcount > 0:
            quit()

        return errorcount == 0