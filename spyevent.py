import time
from os.path import exists

from rocalert.captcha.captcha_logger import CaptchaLogger
from rocalert.cookiehelper import (
    load_cookies_from_browser,
    load_cookies_from_path,
    save_cookies_to_path,
)
from rocalert.events import SpyEvent
from rocalert.roc_settings import SettingsSetupHelper, UserSettings
from rocalert.roc_web_handler import RocWebHandler
from rocalert.rocaccount import BattlefieldTarget
from rocalert.services.urlgenerator import ROCDecryptUrlGenerator

lower_rank_cutoff = 1
upper_rank_cutoff = None

# Comma separated ids. Put your own ID in here
skip_ids = {7530}
skip_ranks = {112}

reversed_order = True


# This will only spy on selected IDs. Other filters ignored
onlyspy_ids = {}

cookie_filename = "cookies"

captchasavepath = "captcha_img/"
captchaans_log = "logs/spyevent.log"

skip_idsstr = {str(id) for id in skip_ids}
onlyspy_idsstr = {str(id) for id in onlyspy_ids}


def user_filter(user: BattlefieldTarget) -> bool:
    if onlyspy_idsstr and len(onlyspy_idsstr) > 0:
        return user in onlyspy_idsstr

    if (
        lower_rank_cutoff
        and user.rank < lower_rank_cutoff
        or upper_rank_cutoff
        and user.rank > upper_rank_cutoff
    ):
        return False

    return not (user.rank in skip_ranks or user.id in skip_idsstr)


def __load_browser_cookies(roc: RocWebHandler, us: UserSettings) -> bool:
    if us.get_setting("load_cookies_from_browser").value:
        url_generator = ROCDecryptUrlGenerator()
        cookies = load_cookies_from_browser(
            us.get_setting("browser").value, url_generator.get_home()
        )
        roc.add_cookies(cookies)
        time.sleep(0.25)
        return True
    return False


def __load_cookies_file(roc: RocWebHandler, cookie_filename: str) -> bool:
    if exists(cookie_filename):
        print("Loading saved cookies")
        cookies = load_cookies_from_path(cookie_filename)
        if cookies is not None:
            roc.add_cookies(cookies)
    time.sleep(0.25)


def __log(s: str):
    print(s)


def login(roc: RocWebHandler, us: UserSettings):
    __log("Attempting to get login status")
    if __load_cookies_file(roc, cookie_filename) and roc.is_logged_in():
        __log("Successfully used cookie file")
        return True

    if __load_browser_cookies(roc, us) and roc.is_logged_in():
        __log(
            "Successfully pulled cookie from {}".format(us.get_setting("browser").value)
        )
        save_cookies_to_path(roc.get_cookies(), cookie_filename)
        return True

    __log("Logging in..")
    roc.login(us.get_setting("email").value, us.get_setting("password").value)
    time.sleep(0.25)
    if roc.is_logged_in():
        __log("Login success.")
        save_cookies_to_path(roc.get_cookies(), cookie_filename)
        return True
    else:
        __log("Login failure.")
        return False


def runevent_new():
    filepaths = {
        "user": ("user.settings", UserSettings),
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
        return

    user_settings = UserSettings(filepath=filepaths["user"][0])
    url_generator = ROCDecryptUrlGenerator()
    rochandler = RocWebHandler(urlgenerator=url_generator)

    if not login(rochandler, user_settings):
        print("Error logging in.")
        quit()

    captchalogger = CaptchaLogger(captchaans_log)
    event = SpyEvent(
        rochandler,
        user_filter,
        reversed_order,
        captcha_save_path=captchasavepath,
        captchalogger=captchalogger,
    )
    event.start_event()
    save_cookies_to_path(rochandler.get_cookies(), cookie_filename)


runevent_new()
