from datetime import datetime, timedelta
import random
import time
from .roc_settings import SettingsError
from rocalert.pyrocalert import RocAlert
from rocalert.services.remote_lookup import RemoteCaptcha
from rocalert.rocpurchases import ROCBuyer, ROCTrainer
from rocalert.roc_settings import BuyerSettings,\
        SettingsSetupHelper, SiteSettings, UserSettings, TrainerSettings
from rocalert.captcha.captcha_logger import CaptchaLogger
from rocalert.roc_web_handler import RocWebHandler


def run():
    filepaths = {
        'trainer': ('trainer.settings', TrainerSettings),
        'site': ('site.settings', SiteSettings),
        'user': ('user.settings', UserSettings),
        'buyer': ('buyer.settings', BuyerSettings)
    }

    settings_file_error = False

    for settype, infotuple in filepaths.items():
        path, settingtype = infotuple
        if SettingsSetupHelper.needs_setup(path):
            settings_file_error = True
            SettingsSetupHelper.create_default_file(
                path, settingtype.DEFAULT_SETTINGS)
            print(f"Created settings file {path}.")

    if settings_file_error:
        print("Exiting. Please fill out settings files")
        return

    gen_log = CaptchaLogger('logs/captcha_answers.log', timestamp=True)
    correct_log = CaptchaLogger('logs/correct_ans.log', log_correctness=False)

    rochandler = RocWebHandler(SiteSettings(filepath=filepaths['site'][0]))
    user_settings = UserSettings(filepath=filepaths['user'][0])

    remoteCaptcha = RemoteCaptcha(
        user_settings.get_value('remote_captcha_add'),
        user_settings.get_value('remote_captcha_lookup'))

    buyer = ROCBuyer(
        rochandler,
        BuyerSettings(filepath=filepaths['buyer'][0]),
        )

    trainer = ROCTrainer(
        rochandler,
        TrainerSettings(filepath=filepaths['trainer'][0])
    )
    a = RocAlert(
        rochandler,
        user_settings,
        buyer,
        trainer,
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

    base = 5*(max(1, errorcount % 4))
    sleeptime = int(muiltiplier * (base + random.uniform(0, 15)))
    print(f'Sleeping for {sleeptime} minutes')
    time.sleep(sleeptime*60)


def main():
    errorcount = 0
    lasterrortime = datetime.now() - timedelta(minutes=5)
    keeprunning = True
    while keeprunning:
        try:
            run()
            keeprunning = False
        except KeyboardInterrupt:
            print('Detected keyboard interrupt')
            return
        except SettingsError as e:
            print(e)
            return
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
