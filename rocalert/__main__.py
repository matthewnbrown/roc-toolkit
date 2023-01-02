from datetime import datetime, timedelta
import random
import time

from .roc_settings import SettingsError
from rocalert.pyrocalert import RocAlert
from rocalert.configuration import configure_services


_user_settings_fp = 'user.settings'


def _run():
    services = configure_services()

    a = RocAlert(
        rochandler=services['rochandler'],
        usersettings=services['user_settings'],
        buyer=services['buyer'],
        trainer=services['trainer'],
        correctLog=services['correct_captcha_logger'],
        generalLog=services['gen_captcha_logger'],
        remoteCaptcha=services['remote_captcha'],
        capsolver=services['capsolver']
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
