from datetime import datetime, timedelta
import random
import time
from rocalert.pyrocalert import RocAlert
from rocalert.services.remote_lookup import RemoteCaptcha
from rocalert.rocpurchases.roc_buyer import ROCBuyer
from rocalert.roc_settings.settingstools import BuyerSettings,\
        SettingsFileMaker, SiteSettings, UserSettings
from rocalert.captcha.captcha_logger import CaptchaLogger
from rocalert.roc_web_handler import RocWebHandler


def run():
    user_settings_fp = 'user.settings'
    site_settings_fp = 'site.settings'
    buyer_settings_fp = 'buyer.settings'
    trainer_settings_fp = 'trainer.settings'

    if SettingsFileMaker.needs_user_setup(
            user_settings_fp, site_settings_fp,
            buyer_settings_fp, trainer_settings_fp):
        print("Exiting. Please fill out settings files")
        quit()

    gen_log = CaptchaLogger('logs/captcha_answers.log', timestamp=True)
    correct_log = CaptchaLogger('logs/correct_ans.log', log_correctness=False)

    rochandler = RocWebHandler(SiteSettings(filepath=site_settings_fp))
    user_settings = UserSettings(filepath=user_settings_fp)

    remoteCaptcha = RemoteCaptcha(
        user_settings.get_value('remote_captcha_add'),
        user_settings.get_value('remote_captcha_lookup'))

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


def _error_nap(errorcount, timebetweenerrors) -> None:
    muiltiplier = 1
    if timebetweenerrors < timedelta(minutes=5):
        print('Very recent error, increasing sleep time')
        muiltiplier = 2

    base = 10*(1 + errorcount % 4)
    sleeptime = muiltiplier * (base + random.uniform(0, 15))
    print(f'Sleeping for {sleeptime} minutes')
    time.sleep(sleeptime*60)


def main():
    errorcount = 0
    lasterrortime = datetime.now()
    keeprunning = True
    while keeprunning:
        try:
            run()
            keeprunning = False
        except KeyboardInterrupt as e:
            print('Detected keyboard interrupt')
            raise e
        except Exception as e:
            # TODO: Collect specific exceptions and handle them
            # ConnectionResetError
            errorcount += 1
            timebetweenerrors = datetime.now() - lasterrortime
            lasterrortime = datetime.now()
            print(e)
            print(f"\nWarning: Detected exception #{errorcount}")
            _error_nap(errorcount, timebetweenerrors)
            print('\n\nRestarting...')


if __name__ == '__main__':
    exit(main())
