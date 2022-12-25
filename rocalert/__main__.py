from datetime import datetime, timedelta
import random
import time

from .roc_settings import SettingsError
from rocalert.pyrocalert import RocAlert
from rocalert.services.remote_lookup import RemoteCaptcha
import rocalert.services.captchaservices as captchaservices
from rocalert.rocpurchases import ROCBuyer, SimpleRocTrainer
from rocalert.roc_settings import BuyerSettings,\
        SettingsSetupHelper, UserSettings, TrainerSettings
from rocalert.captcha.captcha_logger import CaptchaLogger
from rocalert.roc_web_handler import RocWebHandler
from rocalert.services.urlgenerator import ROCDecryptUrlGenerator

_user_settings_fp = 'user.settings'
_trainer_settings_fp = 'trainer.settings'
_buyer_settings_fp = 'buyer.settings'


def _run():
    if not _settings_are_valid():
        quit()

    user_settings = UserSettings(filepath=_user_settings_fp)

    services = _configure_services(user_settings)

    a = RocAlert(
        rochandler=services['rochandler'],
        usersettings=user_settings,
        buyer=services['buyer'],
        trainer=services['trainer'],
        correctLog=services['correct_captcha_logger'],
        generalLog=services['gen_captcha_logger'],
        remoteCaptcha=services['remote_captcha'],
        capsolver=services['capsolver']
        )

    a.start()


def _settings_are_valid() -> bool:
    filepaths = {
        'trainer': (_trainer_settings_fp, TrainerSettings),
        'user': (_user_settings_fp, UserSettings),
        'buyer': (_buyer_settings_fp, BuyerSettings)
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
        return False

    return True


def _configure_services(user_settings: UserSettings) -> dict[str, object]:
    services = {}

    services['gen_captcha_logger'] = CaptchaLogger(
        'logs/captcha_answers.log', timestamp=True)

    services['correct_captcha_logger'] = CaptchaLogger(
        'logs/correct_ans.log', log_correctness=False)

    services['default_headers'] = _get_default_headers()

    services['remote_captcha'] = RemoteCaptcha(
        user_settings.get_value('remote_captcha_add'),
        user_settings.get_value('remote_captcha_lookup'))

    services['urlgenerator'] = ROCDecryptUrlGenerator()

    if user_settings.get_setting('auto_solve_captchas').value:
        savepath = user_settings.get_setting('captcha_save_path').value
        apikey = user_settings.get_setting('auto_captcha_key').value
        services['capsolver'] = captchaservices.TwocaptchaSolverService(
            api_key=apikey, savepath=savepath)
    else:
        services['capsolver'] = captchaservices.ManualCaptchaSolverService()

    services['rochandler'] = RocWebHandler(
        urlgenerator=services['urlgenerator'],
        default_headers=services['default_headers'])

    services['buyer'] = ROCBuyer(
        services['rochandler'],
        BuyerSettings(filepath=_buyer_settings_fp),
        )

    services['trainer'] = SimpleRocTrainer(
        TrainerSettings(filepath=_trainer_settings_fp)
    )

    return services


def _get_default_headers():
    return {
        'Accept': 'text/html,application/xhtml+xml,application/xml'
                  + ';q=0.9,image/avif,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Connection': 'keep-alive',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'same-origin',
        'Sec-Fetch-User': '?1',
        'TE': 'trailers',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                      + 'AppleWebKit/537.36 (KHTML, like Gecko) '
                      + 'Chrome/107.0.0.0 Safari/537.36',
    }


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
            _run()
            keeprunning = False
        except KeyboardInterrupt as e:
            print('Detected keyboard interrupt')
            raise e
        except SettingsError as e:
            print(f'Settings error: {e}\nExiting..')
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
