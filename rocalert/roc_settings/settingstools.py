from datetime import datetime
from typing import Callable
from urllib.parse import urlparse
import os


class Settings:
    def __init__(self, name: str = None, filepath=None) -> None:
        self.settings = {}
        if name is None:
            name = 'Settings'
        self.name = name
        self.mandatory = set()
        if filepath is not None:
            SettingsLoader.load_settings_from_path(
                filepath, settings=self.settings, warnings=True)

    def load_settings_from_path(self, filepath) -> None:
        SettingsLoader.load_settings_from_path(
            filepath, self.settings, warnings=True)
        SettingsValidator.check_mandatories(
            self.settings, self.mandatory, quit_if_bad=True)

    def get_setting(self, setting) -> None:
        if setting not in self.settings:
            return None
        return self.settings[setting]

    def set_setting(self, setting, value) -> None:
        self.settings[setting] = value

        if setting in self.mandatory:
            SettingsValidator.check_mandatories(
                self.settings, self.mandatory, quit_if_bad=True)

    def print_settings_and_values(self, enumerate: bool = False) -> None:
        print(self.name)
        i = 0
        for setting, value in self.settings.items():
            if enumerate:
                print('{}. '.format(i), end='')

            print('{} : {}'.format(setting, value))

    def print_settings(self, enumerate: bool = False) -> None:
        print(self.name)
        i = 0
        for setting, value in self.settings.items():
            if enumerate:
                print('{}. '.format(i), end='')

            print('{} : {}'.format(setting, value))

    def get_settings(self):
        return self.settings


class BuyerSettings(Settings):

    DEFAULT_SETTINGS = {
        'buy_weapons': False,
        'min_gold': 500000000,
        'dagger': 0,
        'maul': 0,
        'blade': 0,
        'excalibur': 0,
        'cloak': 0,
        'hook': 0,
        'pickaxe': 0,
        'sai': 0,
        'shield': 0,
        'mithril': 0,
        'dragonskin': 0,
        'horn': 0,
        'guard_dog': 0,
        'torch': 0,
    }

    SETTINGS_TYPES = {
        'buy_weapons': bool,
        'min_gold': int,
        'dagger': int,
        'maul': int,
        'blade': int,
        'excalibur': int,
        'cloak': int,
        'hook': int,
        'pickaxe': int,
        'sai': int,
        'shield': int,
        'mithril': int,
        'dragonskin': int,
        'horn': int,
        'guard_dog': int,
        'torch': int
    }

    def __init__(self, name: str = None, filepath=None) -> None:
        if name is None:
            name = "Buyer Settings"
        super().__init__(name, filepath)

        self.mandatory = {'buy_weapons'}

        if(filepath is not None):
            self.__check_valid_settings()

    def load_settings_from_path(self, filepath) -> None:
        super().load_settings_from_path(filepath)
        self.__check_valid_settings()

    def buying_enabled(self) -> bool:
        return self.settings is not None and self.settings['buy_weapons']

    def min_gold_to_buy(self) -> int:
        return self.settings['min_gold']

    def get_weapons_to_buy(self) -> dict:
        d = {}
        for setting, val in self.settings.items():
            if setting != 'buy_weapons' and setting != 'min_gold' and val > 0:
                d[setting] = val
        return d

    def __check_valid_settings(self):
        SettingsValidator.check_mandatories(
            self.settings, self.mandatory, quit_if_bad=True)
        SettingsValidator.set_defaults_ifnotset(
            self.settings,
            {'buy_weapons': BuyerSettings.DEFAULT_SETTINGS['buy_weapons']},
            lambda s: s.lower() == 'true'
            )
        default_ints = BuyerSettings.DEFAULT_SETTINGS.copy()
        del default_ints['buy_weapons']
        SettingsValidator.set_defaults_ifnotset(
            self.settings,
            default_ints,
            lambda i: int(str(i).replace(',', ''))
            )


class UserSettings(Settings):

    DEFAULT_SETTINGS = {
        'email': 'email@email.com',
        'password': 'password123',
        'auto_solve_captchas': 'False',
        'auto_captcha_key': '',
        'notify_soldier_amt': '60',
        'min_checktime_secs': '300',
        'max_checktime_secs': '600',
        'enable_nightmode': 'False',
        'nightmode_minwait_mins': '60',
        'nightmode_maxwait_mins': '120',
        'nightmode_begin': '20:00',
        'nightmode_end': '9:00',
        'max_consecutive_login_failures': '2',
        'max_consecutive_captcha_attempts': '3',
        'max_consecutive_answer_errors': '5',
        'captcha_save_path': r'captcha_img/',
        'load_cookies_from_browser': 'True',
        'browser': 'chrome',
        'remote_captcha_lookup': None,
        'remote_captcha_add': None
    }

    SETTINGS_TYPES = {
        'email': str,
        'password': str,
        'auto_solve_captchas': bool,
        'auto_captcha_key': str,
        'notify_soldier_amt': int,
        'min_checktime_secs': int,
        'max_checktime_secs': int,
        'enable_nightmode': bool,
        'nightmode_minwait_mins': int,
        'nightmode_maxwait_mins': int,
        'nightmode_begin': datetime,
        'nightmode_end': datetime,
        'max_consecutive_login_failures': int,
        'max_consecutive_captcha_attempts': int,
        'max_consecutive_answer_errors': int,
        'captcha_save_path': str,
        'load_cookies_from_browser': bool,
        'browser': str,
        'remote_captcha_lookup': str,
        'remote_captcha_add': str
    }

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
        default_bools = {'auto_solve_captchas': False,
                         'enable_nightmode': False,
                         'load_cookies_from_browser': False}

        default_ints = {'notify_soldier_amt': 60,
                        'min_checktime_secs': 300,
                        'max_checktime_secs': 600,
                        'nightmode_minwait_mins': 60,
                        'nightmode_maxwait_mins': 120,
                        'max_consecutive_login_failures': 2,
                        'max_consecutive_captcha_attempts': 3,
                        'max_consecutive_answer_errors': 5}

        def time_conv(t): return datetime.strptime(t, '%H:%M').time() if len(
            t) <= 5 else datetime.strptime(t, '%H:%M:%S').time()
        default_shorttime = {'nightmode_begin': time_conv(
            '00:00'), 'nightmode_end': time_conv('9:00')}

        SettingsValidator.check_mandatories(
            self.settings, self.mandatory, quit_if_bad=True)
        SettingsValidator.set_defaults_ifnotset(
            self.settings, default_bools, lambda s: s.lower() == 'true')
        SettingsValidator.set_defaults_ifnotset(
            self.settings, default_ints, lambda i: int(i))
        SettingsValidator.set_defaults_ifnotset(
            self.settings, default_shorttime, time_conv)

        if self.get_setting('load_cookies_from_browser'):
            validbrowsers = {'chrome', 'firefox'}
            self.settings['browser'] = self.settings['browser'].lower()
            if self.get_setting('browser') not in validbrowsers:
                print('Warning! load_cookies_from_browser enabled,\
                     but browser \'{}\' is not valid'.format(
                    self.get_setting('browser')))
                print('Cookies will not be loaded!')
                self.settings['load_cookies_from_browser'] = False

        for setting in UserSettings.SETTINGS_TYPES:
            if UserSettings.SETTINGS_TYPES[setting] == str \
                    and UserSettings.DEFAULT_SETTINGS[setting] is None:
                SettingsValidator.set_defaults_ifnotset(
                    self.get_settings(),
                    {setting: None},
                    lambda s: None if s.lower() == 'none' else s)


class SiteSettings(Settings):
    DEFAULT_SETTINGS = {
        'roc_home': 'ENTER_HOME_URL',
        'roc_login': 'ENTER_LOGIN_URL',
        'roc_recruit': 'ENTER_RECRUIT_URL',
        'roc_armory': 'ENTER_ARMORY_URL'
    }

    SETTINGS_TYPES = {
        'roc_home': str,
        'roc_login': str,
        'roc_recruit': str,
        'roc_armory': str
    }

    def __init__(self, name: str = None, filepath=None) -> None:
        if name is None:
            name = 'Site Settings'
        super().__init__(name, filepath)

        self.mandatory = {'roc_home', 'roc_home', 'roc_home'}

        if filepath is not None:
            SettingsValidator.check_mandatories(
                self.settings, self.mandatory, quit_if_bad=True)
            validUrls = SettingsValidator.validate_set(
                self.settings, self.mandatory, SiteSettings.__url_valid)

            if not validUrls:
                print(
                    'Site settings are not set correctly. '
                    + 'Ensure URLs are valid. Exiting')
                quit()

    def __url_valid(urlstr: str) -> bool:
        try:
            result = urlparse(urlstr)
            return all([result.scheme, result.netloc])
        except ValueError:
            return False


class SettingsLoader:
    def load_settings_from_path(filepath,
                                settings: dict = None,
                                warnings: bool = False
                                ) -> dict:
        if settings is None:
            settings = {}

        with open(filepath) as f:
            lines = f.readlines()

        for line in lines:
            line = SettingsLoader.__split_comment(line)

            if ':' not in line:
                continue

            setting_name, value = line.split(':', maxsplit=1)
            setting_name = setting_name.strip()
            value = value.strip()
            if warnings and setting_name == '':
                print("Warning: A setting existed with no value")
                continue
            if warnings and len(value) == 0:
                print("Warning: setting {} has no value".format(setting_name))
                continue
            settings[setting_name] = value

    def __split_comment(line: str) -> str:
        return line.split('#', maxsplit=1)[0]


class SettingsSaver:
    def __make_str(key, val) -> str:
        return '{}:{}\n'.format(key, val)

    def __make_lines(settings: dict):
        arr = []
        for key, val in settings.items():
            arr.append(SettingsSaver.__make_str(key, val))
        return arr

    def save_settings_toPath(filepath: str, settings: dict) -> None:
        lines = SettingsSaver.__make_lines(settings)

        with open(filepath, 'w') as f:
            f.writelines(lines)


class SettingsValidator:
    def __check_dict_generic(setdic, key, default, callback: Callable) -> None:
        if key not in setdic:
            setdic[key] = default
        else:
            setdic[key] = callback(setdic[key])

    def validate_set(settings: dict,
                     settings_to_validate,
                     validationfunc: Callable
                     ) -> bool:
        for item in settings_to_validate:
            if item not in settings or not validationfunc(settings[item]):
                return False
        return True

    def set_defaults_ifnotset(settings: dict,
                              defaults: dict,
                              callback: callable
                              ) -> None:
        if settings is None or defaults is None or callback is None:
            return

        for key, val in defaults.items():
            SettingsValidator.__check_dict_generic(
                settings, key, val, callback)

    # Return true if all mandatories are set
    def check_mandatories(settings: dict,
                          mandatories,
                          printError: bool = True,
                          quit_if_bad=False
                          ) -> bool:
        if settings is None or mandatories is None:
            return False

        errorcount = 0
        for setting in mandatories:
            if setting not in settings\
                    or settings[setting] is None\
                    or len(settings[setting]) == 0:
                if printError:
                    print("ERROR: {} setting not set!".format(setting))
                errorcount += 1

        if quit_if_bad and errorcount > 0:
            quit()

        return errorcount == 0


# creates default settings file if the user has yet to do so
class SettingsFileMaker:
    def needs_user_setup(usersettings_fp: str,
                         sitesettings_fp: str,
                         buyersettings_fp: str
                         ) -> bool:
        has_user_settings = os.path.isfile(usersettings_fp)
        has_site_settings = os.path.isfile(sitesettings_fp)
        has_buy_settings = os.path.isfile(buyersettings_fp)

        if has_user_settings and has_site_settings and has_buy_settings:
            return False

        print('You are missing necessary settings files, '
              + 'generic files will be created if needed')

        if not has_user_settings:
            settings = UserSettings.DEFAULT_SETTINGS
            SettingsSaver.save_settings_toPath(usersettings_fp, settings)
            print('Created user settings file {}'.format(usersettings_fp))

        if not has_site_settings:
            settings = SiteSettings.DEFAULT_SETTINGS
            SettingsSaver.save_settings_toPath(sitesettings_fp, settings)
            print('Created site settings file {}'.format(sitesettings_fp))

        if not has_buy_settings:
            settings = BuyerSettings.DEFAULT_SETTINGS
            SettingsSaver.save_settings_toPath(buyersettings_fp, settings)
            print('Created buyer settings file {}'.format(buyersettings_fp))

        return True
