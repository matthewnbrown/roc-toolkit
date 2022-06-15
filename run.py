from math import trunc
from rocalert.pyrocalert import RocAlert
from rocalert.roc_settings.settingstools import SettingsFileMaker, SiteSettings, UserSettings
from rocalert.captcha.captcha_logger import CaptchaLogger
from rocalert.roc_web_handler import Captcha

if __name__== '__main__':
    user_settings_fp = 'user.settings'
    site_settings_fp = 'site.settings'

    if SettingsFileMaker.needs_user_setup(user_settings_fp, site_settings_fp):
        print("Exiting. Please fill out settings files")
        quit()

    gen_log = CaptchaLogger('logs/captcha_answers.log', timestamp=True)
    correct_log = CaptchaLogger('logs/correct_ans.log', log_correctness=False)

    us = UserSettings(filepath=user_settings_fp)
    site = SiteSettings(filepath=site_settings_fp)

    a = RocAlert(us, site,correct_log, gen_log)

    a.start()