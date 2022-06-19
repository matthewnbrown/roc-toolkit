from math import trunc
from rocalert.pyrocalert import RocAlert
from rocalert.remote_lookup import RemoteCaptcha
from rocalert.roc_settings.settingstools import SettingsFileMaker, SiteSettings, UserSettings
from rocalert.captcha.captcha_logger import CaptchaLogger

if __name__== '__main__':
    user_settings_fp = 'user.settings'
    site_settings_fp = 'site.settings'

    remoteCaptchaLookup = None
    remoteCaptchaAdd = None

    if SettingsFileMaker.needs_user_setup(user_settings_fp, site_settings_fp):
        print("Exiting. Please fill out settings files")
        quit()

    gen_log = CaptchaLogger('logs/captcha_answers.log', timestamp=True)
    correct_log = CaptchaLogger('logs/correct_ans.log', log_correctness=False)
    remoteCaptcha = RemoteCaptcha(remoteCaptchaAdd, remoteCaptchaLookup)
    us = UserSettings(filepath=user_settings_fp)
    site = SiteSettings(filepath=site_settings_fp)

    a = RocAlert(us, site,correct_log, gen_log, remoteCaptcha)

    a.start()