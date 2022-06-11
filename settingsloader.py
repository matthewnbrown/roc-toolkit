from datetime import datetime

class Settings:
    def __init__(self, name: str = None, filepath = None) -> None:
        self.settings = {}
        if name is None:
            name = 'Settings'
        self.name = name

        if filepath is not None:
            SettingsLoader.load_settings_from_path(filepath, settings=self.settings, warnings=True)         

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


class UserSettings(Settings):
    def __init__(self, name: str = None, filepath=None) -> None:
        if name is None:
            name = 'User Settings'
        super().__init__(name, filepath)

        mandatory = mandatory_user_settings = ['email', 'password']
        default_bools = { 'auto_solve_captchas':False, 'enable_nightmode': False }
        default_ints = {'notify_soldier_amt':60, 'min_checktime_secs':300, 'max_checktime_secs':600,
        'nightmode_minwait_mins': 60, 'nightmode_maxwait_mins':120 }
        default_shorttime = {'nightmode_begin': '00:00', 'nightmode_end': '9:00'}

        if filepath is not None:
            mandiesSet = SettingsValidator.check_mandatories(self.settings, mandatory)
            SettingsValidator.set_defaults_ifnotset(self.settings, default_bools, 'bool')
            SettingsValidator.set_defaults_ifnotset(self.settings, default_ints, 'int')
            SettingsValidator.set_defaults_ifnotset(self.settings, default_shorttime, 'shorttime')

            if not mandiesSet:
                quit()
    
    def get_settings(self):
        return self.settings

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
        
    def __check_dict_int(setdic, key, default) -> None:
        if key not in setdic:
            setdic[key] = default
        else:
            setdic[key] = int(setdic[key])
    def __check_dict_bool(setdic, key, default = False) -> None:
        if key not in setdic:
            setdic[key] = default
        else:
            setdic[key] = setdic[key].lower() == 'true'
    def __check_dict_datetime(setdic, key, default) -> None:
        if key not in setdic:
            setdic[key] = datetime.strptime(default, '%H:%M').time()
        else:
            setdic[key] = datetime.strptime(setdic[key],'%H:%M').time();

    def set_defaults_ifnotset(settings: dict, defaults: dict, deftype: str) -> None:
        if settings is None or defaults is None:
            return

        if deftype == 'int':
            func = SettingsValidator.__check_dict_int
        elif deftype == 'bool':
            func = SettingsValidator.__check_dict_bool
        elif deftype == 'shorttime':
            func = SettingsValidator.__check_dict_datetime
        else:
            func = None
        
        if func is None:
            return
        
        for key, val in defaults.items():
            func(settings, key, val)

    # Return true if all mandatories are set
    def check_mandatories(settings: dict, mandatories, printError: bool = True) -> bool:
        if settings is None or mandatories is None:
            return False

        errorcount = 0
        for setting in mandatories:
            if setting not in settings or settings[setting] is None or len(settings[setting]) == 0:
                if printError:
                    print("ERROR: {} setting not set!".format(setting))
                errorcount += 1
        
        return errorcount == 0
        


# Loads settings from a filepath in setting:value format
# if must_match is true, then a settings_dict must be passed. Values will only be UPDATED
# if must_have_value is true then if
def load_settings(filepath, settings_dict = None, must_match = False, must_have_value = False) -> dict:
    if settings_dict is None:
        settings_dict = {}

    with open(filepath) as f:
        lines = f.readlines()

        for line in lines:
            setting_name, value = line.split(':',maxsplit=1)
            setting_name = setting_name.strip()
            value = value.strip()
            if must_match and setting_name not in settings_dict:
                continue
            if setting_name == '':
                print("Warning: A setting existed with no value")
                continue
            if must_have_value and value == '':
                print("Warning: setting {} has no value".format(setting_name))
                continue
            settings_dict[setting_name] = value
                
    return settings_dict


# loads user settings, does some checks and casts
def load_user_settings(filepath, settings_dict = None) -> dict:
    settings_dict = load_settings(filepath, settings_dict)

    mandatory_user_settings = ['email', 'password']

    errorcount = 0
    for setting in mandatory_user_settings:
        if setting not in settings_dict:
            print("ERROR: {} setting not set!".format(setting))
            errorcount += 1
    
    if errorcount > 0:
        quit()

    default_bools = { 'auto_solve_captchas':False, 'enable_nightmode': False }
    for key, val in default_bools.items():
        Settings.__check_dict_bool(settings_dict, key, val)

    default_ints = {'notify_soldier_amt':60, 'min_checktime_secs':300, 'max_checktime_secs':600,
        'nightmode_minwait_mins': 60, 'nightmode_maxwait_mins':120 }

    for key,val in default_ints.items():
        Settings.__check_dict_int(settings_dict, key, val)

    default_datetime = {'nightmode_begin': '00:00', 'nightmode_end': '9:00'}
    for key,val in default_datetime.items():
        Settings.__check_dict_datetime(settings_dict, key, val)

    return settings_dict