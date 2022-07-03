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

    if SettingsFileMaker.needs_user_setup(
            user_settings_fp, site_settings_fp, buyer_settings_fp):
        print("Exiting. Please fill out settings files")
        quit()

    gen_log = CaptchaLogger('logs/captcha_answers.log', timestamp=True)
    correct_log = CaptchaLogger('logs/correct_ans.log', log_correctness=False)

    rochandler = RocWebHandler(SiteSettings(filepath=site_settings_fp))
    user_settings = UserSettings(filepath=user_settings_fp)

    remoteCaptcha = RemoteCaptcha(
        user_settings.get_setting('remote_captcha_add'),
        user_settings.get_setting('remote_captcha_lookup'))

    buyer = ROCBuyer(
        rochandler,
        BuyerSettings(filepath=buyer_settings_fp),
        )

    a = RocAlert(
        rochandler,
        user_settings,
        buyer,
        correct_log,
        gen_log,
        remoteCaptcha
        )

    a.start()
