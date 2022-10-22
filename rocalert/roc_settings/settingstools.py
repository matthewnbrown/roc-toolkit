import copy
from datetime import datetime as dt, time
from typing import Callable
from urllib.parse import urlparse
import os


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
            self.settings = copy.deepcopy(Settings.DEFAULT_SETTINGS)
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


class BuyerSettings(Settings):
    def __positive__(x): return x >= 0

    DEFAULT_SETTINGS = {
        'buy_weapons': Setting('Toggle Buying', 'buy_weapons', False, bool,
                               'Enable weapon buying'),
        'min_gold': Setting('Minimum Gold', 'min_gold', 500000000, int,
                            'Minimum gold to purchase with',
                            None, __positive__),
        'dagger': Setting('Dagger', 'dagger', 0, int,
                          'Amount of daggers to buy',
                          None, __positive__),
        'maul': Setting('Maul', 'maul', 0, int, 'Amount of Mauls to buy',
                        None, __positive__),
        'blade': Setting('Blade', 'blade', 0, int, 'Amount of blades to buy',
                         None, __positive__),
        'excalibur': Setting('Excalibur', 'excalibur', 0, int,
                             'Amount of excalibur to buy',
                             None, __positive__),
        'cloak': Setting('Cloak', 'cloak', 0, int, 'Amount of cloaks to buy',
                         None, __positive__),
        'hook': Setting('Hook', 'hook', 0, int, 'Amount of hooks to buy',
                        None, __positive__),
        'pickaxe': Setting('Pickaxe', 'pickaxe', 0, int,
                           'Amount of pickaxes to buy',
                           None, __positive__),
        'sai': Setting('Sai', 'sai', 0, int, 'Amount of sai to buy',
                       None, __positive__),
        'shield': Setting('Shield', 'shield', 0, int,
                          'Amount of shields to buy',
                          None, __positive__),
        'mithril': Setting('Mithril', 'mithril', 0, int,
                           'Amount of mithril to buy',
                           None, __positive__),
        'dragonskin': Setting('Dragonskin', 'dragonskin', 0, int,
                              'Amount of dragonskins to buy',
                              None, __positive__),
        'horn': Setting('Horn', 'horn', 0, int, 'Amount of horns to buy',
                        None, __positive__),
        'guard_dog': Setting('Guard Dog', 'guard_dog', 0, int,
                             'Amount of guard dogs to buy',
                             None, __positive__),
        'torch': Setting('Torch', 'torch', 0, int, 'Amount of torches to buy',
                         None, __positive__)
    }

    def __init__(self, name: str = None, filepath=None) -> None:
        if name is None:
            name = "Buyer Settings"

        self.settings = BuyerSettings.DEFAULT_SETTINGS

        super().__init__(name, filepath)

        self.mandatory = {'buy_weapons'}

        if(filepath is not None):
            self.__check_valid_settings()

    def load_settings_from_path(self, filepath) -> None:
        super().load_settings_from_path(filepath)
        self.__check_valid_settings()

    def buying_enabled(self) -> bool:
        return self.settings is not None and self.settings['buy_weapons'].value

    def min_gold_to_buy(self) -> int:
        return self.settings['min_gold'].value

    def get_weapons_to_buy(self) -> dict:
        d = {}
        for settingid, setting in self.settings.items():
            if settingid != 'buy_weapons' and settingid != 'min_gold' \
                    and setting.value > 0:
                d[settingid] = setting.value
        return d

    def __check_valid_settings(self):
        SettingsValidator.check_mandatories(
            self.settings, self.mandatory, quit_if_bad=True)
        SettingsValidator.check_settings_in_range(self.settings, True)


class TrainerSettings(Settings):
    DEFAULT_SETTINGS = {
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
            None,
            lambda x: x in ['attack', 'defense', 'spy', 'sentry', 'none']
        )
    }

    class SoldierTypes:
        ATTACK = 'attack'
        DEFENSE = 'defense'
        SPY = 'spy'
        SENTRY = 'sentry'
        NONE = 'none'

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
                    time_conv('20:00'), time,
                    'Start time of nightmode format HH:MM:SS'),
        'nightmode_end':
            Setting('Nightmode end time', 'nightmode_end',
                    time_conv('08:00'), time,
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
            Setting('Max repeated bad captcha answers',
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
                    None,
                    lambda x: x in ['all', 'chrome', 'firefox', 'opera', 'edge'
                                    'chromium', 'brave', 'vivaldi', 'safari']),
        'remote_captcha_lookup':
            Setting('Remote captcha lookup API address',
                    'remote_captcha_lookup', None, str,
                    'URL to API for captcha answer lookup'),
        'remote_captcha_add':
            Setting('Remote captcha add API address', 'remote_captcha_add',
                    None, str, 'URL to API to add captcha answer'),
        'captcha_failure_timeout':
            Setting('Captcha failure timeout length',
                    'captcha_failure_timeout', 0, int,
                    'Amount of time to wait after captcha error limit'
                    + ' reached. 0 to exit instead of timeout')
    }

    def __init__(self, name: str = None, filepath=None) -> None:
        if name is None:
            name = 'User Settings'

        self.settings = copy.deepcopy(UserSettings.DEFAULT_SETTINGS)

        super().__init__(name, filepath)

        self.mandatory = {'email', 'password'}

        if filepath is not None:
            self.__check_valid_settings()

    def load_settings_from_path(self, filepath) -> None:
        super().load_settings_from_path(filepath)
        self.__check_valid_settings()

    def __check_valid_settings(self):
        SettingsValidator.check_mandatories(
            self.settings, self.mandatory, quit_if_bad=True)
        inrange = SettingsValidator.check_settings_in_range(
            self.settings, warnings=True)

        if not inrange:
            print("ERROR: User settings are invalid!")
            quit()

        savepath = self.get_value('captcha_save_path')
        if not os.path.exists(savepath):
            print(f'Warning: path {savepath} does not exist.'
                  + ' Creating directories.')
            os.makedirs(savepath)

    def auto_solve_captchas(self) -> bool:
        return self.get_value('auto_solve_captchas')

    def auto_solve_api_key(self) -> str:
        return self.get_value('auto_captcha_key')


def __validurl__(urlstr: str) -> bool:
    try:
        result = urlparse(urlstr)
        return all([result.scheme, result.netloc])
    except ValueError:
        return False


class SiteSettings(Settings):
    DEFAULT_SETTINGS = {
        'roc_home':
            Setting('ROC Index Page', 'roc_home', 'ENTER_HOME_URL',
                    str, 'Index page of ROC.',
                    validation_func=__validurl__),
        'roc_login':
            Setting('ROC Login Page', 'roc_login', 'ENTER_LOGIN_URL',
                    str, 'Login page likely homepage + /login.php',
                    validation_func=__validurl__),
        'roc_recruit':
            Setting('ROC Recruit Page', 'roc_recruit', 'ENTER_RECRUIT_URL',
                    str, 'Recruit captcha page',
                    validation_func=__validurl__),
        'roc_armory':
            Setting('ROC Armory Page', 'roc_armory', 'ENTER_ARMORY_URL',
                    str, 'Armory page of ROC',
                    validation_func=__validurl__),
        'roc_training':
            Setting('ROC Training Page', 'roc_training', 'ENTER_TRAINING_URL',
                    str, 'Soldier training page',
                    validation_func=__validurl__)
    }

    def __init__(self, name: str = None, filepath: str = None) -> None:
        if name is None:
            name = 'Site Settings'

        self.settings = copy.deepcopy(SiteSettings.DEFAULT_SETTINGS)

        super().__init__(name, filepath)

        self.mandatory = {'roc_home', 'roc_recruit'}

        if filepath is not None:
            SettingsValidator.check_mandatories(
                self.settings, self.mandatory, quit_if_bad=True)
            validUrls = True

            for id, setting in self.settings.items():
                if id not in SiteSettings.DEFAULT_SETTINGS:
                    continue
                url = setting.value

                validurl = setting.validation_func(url)
                if not validurl:
                    print(f'{setting.pname} is invalid')

                validUrls &= validurl

            if not validUrls:
                print(
                    'Site settings are not set correctly. '
                    + 'Ensure URLs are valid. Exiting')
                quit()

    def get_page(self, page: str) -> str:
        return self.get_value(page)

    def get_home(self) -> str:
        return self.get_page('roc_home')

    def get_recruit(self) -> str:
        return self.get_page('roc_recruit')

    def get_armory(self) -> str:
        return self.get_page('roc_armory')

    def get_training(self) -> str:
        return self.get_page('roc_training')

    def get_login_url(self) -> str:
        return self.get_page('roc_login')


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

    def __tobool__(value: str) -> bool:
        value = value.lower()
        validans = ['yes', 'y', 'true', 'enable', 'enabled']
        return value in validans

    __convmap__ = {
        str: __tostr__,
        int: __toint__,
        time: __totime__,
        bool: __tobool__
        }


class SettingsLoader:
    def load_settings_from_path(filepath,
                                settings: dict[str, Setting] = None,
                                warnings: bool = False
                                ) -> dict:
        if settings is None:
            if warnings:
                print('Warning. Empty settings file passed to loader')
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
                print("Warning: A setting existed with no name")
                continue
            if warnings and len(value) == 0:
                print("Warning: setting {} has no value".format(setting_name))
                continue
            if setting_name not in settings:
                settings[setting_name] = Setting(
                    setting_name, setting_name)
                if warnings:
                    print(f"Warning: Setting {setting_name} found "
                          + "that is not in defaults")

            if setting_name in settings:
                setting = settings[setting_name]
            else:
                setting = Setting(setting_name, setting_name, value=value)
            setting.value = SettingsConverter.convert(value, setting.valtype)

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
    def __check_dict_generic(setdic, key, default, callback: Callable) -> None:
        if key not in setdic:
            print(f"Warning: setting {key} not in settings."
                  + f" Set to default value: {default}")
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
            curvalid = type(setting.value) == setting.valtype
            if setting.validation_func:
                curvalid &= setting.validation_func(setting.value)

            if warnings and not curvalid:
                print(f'Warning: Settings {settingid} value is invalid')

            valid &= curvalid
        return valid


# creates default settings file if the user has yet to do so
class SettingsFileMaker:
    def needs_user_setup(usersettings_fp: str = None,
                         sitesettings_fp: str = None,
                         buyersettings_fp: str = None,
                         trainsettings_fp: str = None
                         ) -> bool:
        has_user_settings = usersettings_fp is None \
            or os.path.isfile(usersettings_fp)
        has_site_settings = sitesettings_fp is None \
            or os.path.isfile(sitesettings_fp)
        has_buy_settings = buyersettings_fp is None \
            or os.path.isfile(buyersettings_fp)
        has_train_settings = trainsettings_fp is None \
            or os.path.isfile(trainsettings_fp)

        if has_user_settings and has_site_settings \
                and has_buy_settings and has_train_settings:
            return False

        print('You are missing necessary settings files, '
              + 'generic files will be created if needed')

        if usersettings_fp and not has_user_settings:
            settings = UserSettings.DEFAULT_SETTINGS
            SettingsSaver.save_settings_toPath(usersettings_fp, settings)
            print('Created user settings file {}'.format(usersettings_fp))

        if sitesettings_fp and not has_site_settings:
            settings = SiteSettings.DEFAULT_SETTINGS
            SettingsSaver.save_settings_toPath(sitesettings_fp, settings)
            print('Created site settings file {}'.format(sitesettings_fp))

        if buyersettings_fp and not has_buy_settings:
            settings = BuyerSettings.DEFAULT_SETTINGS
            SettingsSaver.save_settings_toPath(buyersettings_fp, settings)
            print('Created buyer settings file {}'.format(buyersettings_fp))

        if trainsettings_fp and not has_train_settings:
            settings = TrainerSettings.DEFAULT_SETTINGS
            SettingsSaver.save_settings_toPath(trainsettings_fp, settings)
            print(f'Created trainer settings file {trainsettings_fp}')

        return True
