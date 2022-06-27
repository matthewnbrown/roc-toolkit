from rocalert.pyrocalert import RocAlert
from rocalert.remote_lookup import RemoteCaptcha
from rocalert.roc_buyer import ROCBuyer
from rocalert.roc_settings.settingstools import BuyerSettings,\
        SettingsFileMaker, SiteSettings, UserSettings
from rocalert.captcha.captcha_logger import CaptchaLogger
from rocalert.roc_web_handler import RocWebHandler

if __name__ == '__main__':
    user_settings_fp = 'user.settings'
    site_settings_fp = 'site.settings'
    buyer_settings_fp = 'buyer.settings'

    remoteCaptchaLookup = None
    remoteCaptchaAdd = None

    if SettingsFileMaker.needs_user_setup(
            user_settings_fp, site_settings_fp, buyer_settings_fp):
        print("Exiting. Please fill out settings files")
        quit()

    gen_log = CaptchaLogger('logs/captcha_answers.log', timestamp=True)
    correct_log = CaptchaLogger('logs/correct_ans.log', log_correctness=False)
    remoteCaptcha = RemoteCaptcha(remoteCaptchaAdd, remoteCaptchaLookup)

    rochandler = RocWebHandler(SiteSettings(filepath=site_settings_fp))

    us = UserSettings(filepath=user_settings_fp)
    buyer = ROCBuyer(
        rochandler,
        BuyerSettings(filepath=buyer_settings_fp),
        correct_log, gen_log)
    a = RocAlert(rochandler, us, buyer, correct_log, gen_log, remoteCaptcha)

    a.start()
