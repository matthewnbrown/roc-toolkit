import random
import time
from datetime import datetime, timedelta

import rocalert.services.captchaservices as captchaservices
from rocalert.captcha.captcha_logger import CaptchaLogger
from rocalert.pyrocalert import RocAlert
from rocalert.roc_settings import (
    BuyerSettings,
    SettingsSetupHelper,
    TrainerSettings,
    UserSettings,
)
from rocalert.roc_settings._settings import is_negative_string
from rocalert.roc_web_handler import RocWebHandler
from rocalert.rocpurchases import ROCBuyer, SimpleRocTrainer
from rocalert.services.remote_lookup import RemoteCaptcha
from rocalert.services.urlgenerator import ROCDecryptUrlGenerator
from rocalert.services.useragentgenerator import (
    Browser,
    OperatingSystem,
    UserAgentGenerator,
)
from rocalert.services.exception_handler import ExceptionHandler

from .roc_settings import SettingsError

_user_settings_fp = "user.settings"
_trainer_settings_fp = "trainer.settings"
_buyer_settings_fp = "buyer.settings"


def _run():
    if not _settings_are_valid():
        quit()

    user_settings = UserSettings(filepath=_user_settings_fp)

    services = _configure_services(user_settings)

    a = RocAlert(
        rochandler=services["rochandler"],
        usersettings=user_settings,
        buyer=services["buyer"],
        trainer=services["trainer"],
        correctLog=services["correct_captcha_logger"],
        generalLog=services["gen_captcha_logger"],
        remoteCaptcha=services["remote_captcha"],
        capsolver=services["capsolver"],
    )

    a.start()


def _settings_are_valid() -> bool:
    filepaths = {
        "trainer": (_trainer_settings_fp, TrainerSettings),
        "user": (_user_settings_fp, UserSettings),
        "buyer": (_buyer_settings_fp, BuyerSettings),
    }

    settings_file_error = False

    for settype, infotuple in filepaths.items():
        path, settingtype = infotuple
        if SettingsSetupHelper.needs_setup(path):
            settings_file_error = True
            SettingsSetupHelper.create_default_file(path, settingtype.DEFAULT_SETTINGS)
            print(f"Created settings file {path}.")

    if settings_file_error:
        print("Exiting. Please fill out settings files")
        return False

    return True


def _configure_services(user_settings: UserSettings) -> dict[str, object]:
    services = {}

    services["gen_captcha_logger"] = CaptchaLogger(
        "logs/captcha_answers.log", timestamp=True
    )

    services["correct_captcha_logger"] = CaptchaLogger(
        "logs/correct_ans.log", log_correctness=False
    )

    services["exception_handler"] = ExceptionHandler()

    services["default_headers"] = _get_default_headers()

    services["remote_captcha"] = RemoteCaptcha(
        user_settings.get_value("remote_captcha_add"),
        user_settings.get_value("remote_captcha_lookup"),
    )

    services["urlgenerator"] = ROCDecryptUrlGenerator()

    services["capsolver"] = _get_captcha_solving_service(user_settings)

    services["rochandler"] = RocWebHandler(
        urlgenerator=services["urlgenerator"],
        default_headers=services["default_headers"],
    )

    services["buyer"] = ROCBuyer(
        services["rochandler"],
        BuyerSettings(filepath=_buyer_settings_fp),
    )

    services["trainer"] = SimpleRocTrainer(
        TrainerSettings(filepath=_trainer_settings_fp)
    )

    return services


def _get_captcha_solving_service(user_settings: UserSettings):
    service = user_settings.get_setting("auto_solve_captchas").value.lower().strip()

    savepath = user_settings.get_setting("captcha_save_path").value

    if is_negative_string(service):
        return captchaservices.ManualCaptchaSolverService()

    captcha_settings = captchaservices.get_captcha_settings(service)
    if captcha_settings is None:
        filename = captchaservices.create_captca_settings_file(service)
        print(f"Created settings file {filename}. Please fill it out and restart")
        quit()

    if service in ["2captcha", "twocaptcha"]:
        apikey = captcha_settings["apiKey"]
        return captchaservices.TwocaptchaSolverService(
            api_key=apikey, savepath=savepath
        )
    if service in ["truecaptcha", "true captcha"]:
        return captchaservices.TrueCaptchaSolverService(
            userid=captcha_settings["userId"],
            api_key=captcha_settings["apiKey"],
            mode=captcha_settings["mode"],
            savepath=savepath,
        )
    if service in ["rocapi", "ai"]:
        base_url = captcha_settings["base_url"]
        return captchaservices.RemoteCaptchaSolverService(
            solve_url=base_url + captcha_settings["solve_url"],
            report_url=base_url + captcha_settings["report_url"],
        )
           
def _get_default_headers():
    default_agent = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        + "AppleWebKit/537.36 (KHTML, like Gecko) "
        + "Chrome/114.0.0.0 Safari/537.36"
    )
    agentgenerator = UserAgentGenerator(default=default_agent)
    useragent = agentgenerator.get_useragent(
        browser=Browser.Chrome, operatingsystem=OperatingSystem.Windows
    )

    print(f'Using user-agent: "{useragent}"')
    return {
        "Accept": "text/html,application/xhtml+xml,application/xml"
        + ";q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Connection": "keep-alive",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "same-origin",
        "Sec-Fetch-User": "?1",
        "TE": "trailers",
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": useragent,
    }


def _error_nap(errorcount, timebetweenerrors) -> None:
    muiltiplier = 1
    if timebetweenerrors < timedelta(minutes=5):
        print("Very recent error, increasing sleep time")
        muiltiplier = 2

    base = 5 * (max(1, errorcount % 4))
    sleeptime = int(muiltiplier * (base + random.uniform(0, 15)))
    print(f"Sleeping for {sleeptime} minutes")
    time.sleep(sleeptime * 60)


def main():  
    if not _settings_are_valid():
        return
    
    keeprunning = True
    
    # Load user settings for exception handling configuration
    user_settings = UserSettings(filepath=_user_settings_fp)
    enable_exception_timeout = user_settings.exception_timeout_enabled
    exception_timeout_minutes = user_settings.exception_timeout_delay_minutes
    
    # Initialize exception handler
    exception_handler = ExceptionHandler()
    
    while keeprunning:
        try:
            _run()
            keeprunning = False
        except KeyboardInterrupt as e:
            print("Detected keyboard interrupt")
            raise e
        except SettingsError as e:
            print(f"Settings error: {e}\nExiting..")
            return
        except Exception as e:
            # Use the exception handler to manage the exception
            should_continue = exception_handler.handle_exception(
                exception=e,
                enable_timeout=enable_exception_timeout,
                timeout_minutes=exception_timeout_minutes
            )
            
            if not should_continue:
                return  # Exit program/
            
            # If timeout is disabled, use the old error handling method
            if not enable_exception_timeout:
                error_stats = exception_handler.get_error_stats()
                _error_nap(error_stats['error_count'], error_stats['time_since_last_error'])
            
            print("\nRestarting...")


if __name__ == "__main__":
    exit(main())
