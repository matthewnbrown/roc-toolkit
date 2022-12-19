from ._settings import Setting, Settings, SettingsValidator, time_conv
from datetime import time
import os


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
                    100, float, 'Minimum MINUTES to wait during nightmode'),
        'nightmode_maxwait_mins':
            Setting('Nightmode maxmimum wait time', 'nightmode_maxwait_mins',
                    200, float, 'Maximum MINUTE to wait during nightmode'),
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

    def use_nightmode(self) -> bool: return self.settings['enable_nightmode']

    @property
    def nightmode_waittime_range(self) -> tuple(float, float):
        return (self.get_setting('nightmode_minwait_mins'),
                self.get_setting('nightmode_maxwait_mins'))

    @property
    def nightmode_activetime_range(self) -> tuple(time, time):
        return (self.get_setting('nightmode_begin'),
                self.get_setting('nightmode_end'))
