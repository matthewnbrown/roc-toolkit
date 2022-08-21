from datetime import datetime
from typing import Callable, List
from urllib.parse import urlparse
import os


class Setting:
    def __init__(self,
                 prettyname: str,
                 name: str,
                 default_value,
                 valtype: type = None,
                 description: str = None,
                 value=None,
                 valid_values: List = None) -> None:
        self.pname = prettyname
        self.name = name
        self.defaultval = default_value
        self.value = value if value else default_value
        self.valtype = valtype
        self.desc = description

        if type(valtype) != type:
            print(f'Warning: {name} setting valtype is not a valid type.')
        elif type(value) != valtype:
            print(f'Warning: {name} setting type does not match value type.')


class Settings:
    setting_map = {}
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

    setting_map = {
        'buy_weapons': Setting('Toggle Buying', 'buy_weapons', False, bool,
                               'Enable weapon buying'),
        'min_gold': Setting('Minimum Gold', 'min_gold', 500000000, int,
                            'Minimum gold to purchase with'),
        'dagger': Setting('Dagger', 'dagger', 0, int,
                          'Amount of daggers to buy'),
        'maul': Setting('Maul', 'maul', 0, int, 'Amount of Mauls to buy'),
        'blade': Setting('Blade', 'blade', 0, int, 'Amount of blades to buy'),
        'excalibur': Setting('Excalibur', 'excalibur', 0, int,
                             'Amount of excalibur to buy'),
        'cloak': Setting('Cloak', 'cloak', 0, int, 'Amount of cloaks to buy'),
        'hook': Setting('Hook', 'hook', 0, int, 'Amount of hooks to buy'),
        'pickaxe': Setting('Pickaxe', 'pickaxe', 0, int,
                           'Amount of pickaxes to buy'),
        'sai': Setting('Sai', 'sai', 0, int, 'Amount of sai to buy'),
        'shield': Setting('Shield', 'shield', 0, int,
                          'Amount of shields to buy'),
        'mithril': Setting('Mithril', 'mithril', 0, int,
                           'Amount of mithril to buy'),
        'dragonskin': Setting('Dragonskin', 'dragonskin', 0, int,
                              'Amount of dragonskins to buy'),
        'horn': Setting('Horn', 'horn', 0, int, 'Amount of horns to buy'),
        'guard_dog': Setting('Guard Dog', 'guard_dog', 0, int,
                             'Amount of guard dogs to buy'),
        'torch': Setting('Torch', 'torch', 0, int, 'Amount of torches to buy')
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


class TrainerSettings(Settings):
    setting_map = {
        'train_soldiers': Setting(
            'Train Soldiers',
            'train_soldiers',
            False, bool,
            'Enable or disable all soldier training/buying'),
        'soldier_weapon_match': Setting(
            'Match weapons to soldiers',
            'soldier_weapon_match',
            False, bool,
            'Match amount of soldiers to amount of weapons '
            + 'in each weapons program'),
        'soldier_dump_type': Setting(
            'Soldier dump type',
            'soldier_dump_type',
            'none', str,
            'Dump all excess soldiers into this program.',
            valid_values=['attack', 'defense', 'spy', 'sentry', 'none']
        )
    }

    def __init__(self, name: str = None, filepath=None) -> None:
        if name is None:
            name = "Buyer Settings"
        super().__init__(name, filepath)

        self.mandatory = {'train_soldiers'}

        if(filepath is not None):
            self.__check_valid_settings()

    def training_enabled(self):
        return self.set_setting['train_soldiers'].value

    def match_soldiers_to_weapons(self):
        return self.get_setting['soldier_weapon_match'].value

    def soldier_dump_type(self):
        return self.get_setting['soldier_dump_type'].value


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
        'remote_captcha_add': None,
        'captcha_failure_timeout': '0'
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
        'remote_captcha_add': str,
        'captcha_failure_timeout': int
    }

    def time_conv(t: str): return datetime.strptime(t, '%H:%M').time() if len(
            t) <= 5 else datetime.strptime(t, '%H:%M:%S').time()

    setting_map = {
        'email': Setting('Email Address', 'email', 'email@address.com', str,
                         'ROC login email'),
        'password': Setting('Password', 'password', 'password', str,
                            'ROC login password'),
        'auto_solve_captchas':
            Setting('Auto Solve Captchas',
                    'auto_solve_captchas', False, bool,
                    'Automatically solve captchas using a service'),
        'auto_captcha_key': Setting('Autosolve Captcha API Key',
                                    'auto_captcha_key', None, str,
                                    'API key for captcha solving service'),
        'notify_soldier_amt': Setting('Notify soldier amount',
                                      'notify_soldier_amt',
                                      None, int, 'Unused'),
        'min_checktime_secs':
            Setting('Minimum check time', 'min_checktime_secs', 1000, int,
                    'Minimum seconds to wait before an account status check'),
        'max_checktime_secs':
            Setting('Maximum check time', 'max_checktime_secs', 2000, int,
                    'Maximum seconds to wait before an account status check'),
        'enable_nightmode':
            Setting('Enable nightmode', 'enable_nightmode', False, bool,
                    'Enable longer wait times during certain time period'),
        'nightmode_minwait_mins':
            Setting('Nightmode minimum wait time', 'nightmode_minwait_mins',
                    100, int, 'Minimum MINUTES to wait during nightmode'),
        'nightmode_maxwait_mins':
            Setting('Nightmode maxmimum wait time', 'nightmode_maxwait_mins',
                    200, int, 'Maximum MINUTE to wait during nightmode'),
        'nightmode_begin':
            Setting('Nightmode start time', 'nightmode_begin',
                    time_conv('20:00'), datetime,
                    'Start time of nightmode format HH:MM:SS'),
        'nightmode_end':
            Setting('Nightmode end time', 'nightmode_end',
                    time_conv('08:00'), datetime,
                    'End time of nightmode, formatted HH:MM:SS'),
        'max_consecutive_login_failures':
            Setting('Max repeated login attempts',
                    'max_consecutive_login_failures', 2, int,
                    'Max login attempt before terminating program'),
        'max_consecutive_captcha_attempts':
            Setting('Max repeated captcha attempts',
                    'max_consecutive_captcha_attempts', 5, int,
                    'Max attempts of a captcha before timing out or exiting'),
        'max_consecutive_answer_errors':
            Setting('Max repeated bad captcha answers'
                    'max_consecutive_answer_errors', 5, int,
                    'Maximum bad answers to receive before giving up'
                    + '(Not Attempts)'),
        'captcha_save_path':
            Setting('Captcha save path', 'captcha_save_path', r'captcha_img/',
                    str, 'Path to save captcha images to'),
        'load_cookies_from_browser':
            Setting('Load cookies from browser', 'load_cookies_from_browser',
                    False, bool, 'Attempt to retrieve cookies from browser'),
        'browser':
            Setting('Browser choice', 'browser', 'all', str,
                    'Browser to load cookies from',
                    valid_values=['all', 'chrome', 'firefox', 'opera', 'edge'
                                  'chromium', 'brave', 'vivaldi', 'safari']),
        'remote_captcha_lookup':
            Setting('Remote captcha lookup API address', 'remote_captcha_lookup',
                    None, str, 'URL to API for captcha answer lookup'),
        'remote_captcha_add':
            Setting('Remote captcha add API address', 'remote_captcha_add',
                    None, str, 'URL to API to add captcha answer'),
        'captcha_failure_timeout':
            Setting('Captcha failure timeout length', 'captcha_failure_timeout',
                    0, int, 'Amount of time to wait after captcha error limit'
                    + ' reached. 0 to exit instead of timeout')
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
                        'max_consecutive_answer_errors': 5,
                        'captcha_failure_timeout': 0}

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

        for setting in UserSettings.SETTINGS_TYPES:
            if UserSettings.SETTINGS_TYPES[setting] == str \
                    and UserSettings.DEFAULT_SETTINGS[setting] is None:
                SettingsValidator.set_defaults_ifnotset(
                    self.get_settings(),
                    {setting: None},
                    lambda s: None if s.lower() == 'none' else s)

        savepath = self.get_setting('captcha_save_path')
        if not os.path.exists(savepath):
            print(f'Warning path {savepath} does not exist.'
                  + 'Creating directories.')
            os.makedirs(savepath)


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
                         buyersettings_fp: str,
                         trainsettings_fp: str
                         ) -> bool:
        has_user_settings = os.path.isfile(usersettings_fp)
        has_site_settings = os.path.isfile(sitesettings_fp)
        has_buy_settings = os.path.isfile(buyersettings_fp)
        has_train_settings = os.path.isfile(trainsettings_fp)

        if has_user_settings and has_site_settings \
                and has_buy_settings and has_train_settings:
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

        if not has_train_settings:
            smap = TrainerSettings.setting_map
            settings = {id: setting.defaultval for id, setting in smap.items()}
            SettingsSaver.save_settings_toPath(trainsettings_fp, settings)
            print(f'Created trainer settings file {trainsettings_fp}')

        return True
