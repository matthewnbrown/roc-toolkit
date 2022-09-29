from typing import Callable
from os.path import exists

from rocalert.events import SpyEvent
from rocalert.roc_settings.settingstools import SettingsFileMaker, \
    SiteSettings, UserSettings
from rocalert.roc_web_handler import Captcha, RocWebHandler
from rocalert.rocaccount import BattlefieldTarget
from rocalert.cookiehelper import load_cookies_from_path, \
    load_cookies_from_browser, save_cookies_to_path
from rocalert.services.captchaservices import MulticaptchaGUI


lower_rank_cutoff = 1
upper_rank_cutoff = None

# Comma separated ids. Put your own ID in here
skip_ids = {7530}
skip_ranks = {112}

reversed_order = True


# This will only spy on selected IDs. Other filters ignored
onlyspy_ids = {}

cookie_filename = 'cookies'

skip_idsstr = {str(id) for id in skip_ids}
onlyspy_idsstr = {str(id) for id in onlyspy_ids}


def user_filter(user: BattlefieldTarget) -> bool:
    if onlyspy_idsstr and len(onlyspy_idsstr) > 0:
        return user in onlyspy_idsstr

    if lower_rank_cutoff and user.rank < lower_rank_cutoff \
            or upper_rank_cutoff and user.rank > upper_rank_cutoff:
        return False

    return not (user.rank in skip_ranks or user.id in skip_idsstr)


def __load_browser_cookies(roc: RocWebHandler, us: UserSettings) -> bool:
    if us.get_setting('load_cookies_from_browser'):
        cookies = load_cookies_from_browser(
            us.get_setting('browser'),
            roc.site_settings['roc_home']
            )
        roc.add_cookies(cookies)
        return True
    return False


def __load_cookies_file(roc: RocWebHandler, cookie_filename: str) -> bool:
    if exists(cookie_filename):
        print("Loading saved cookies")
        cookies = load_cookies_from_path(cookie_filename)
        if cookies is not None:
            roc.add_cookies(cookies)


def __log(s: str):
    print(s)


def login(roc: RocWebHandler, us: UserSettings):
    __log('Logging in.')
    if __load_cookies_file(roc, cookie_filename) and roc.is_logged_in():
        __log('Successfully used cookie file')
        return True

    if __load_browser_cookies(roc, us) and roc.is_logged_in():
        __log('Successfully pulled cookie from {}'.format(
            us.get_setting('browser')))
        save_cookies_to_path(roc.get_cookies(), cookie_filename)
        return True

    roc.login(
        us.get_setting('email'),
        us.get_setting('password')
    )

    if roc.is_logged_in():
        __log("Login success.")
        save_cookies_to_path(roc.get_cookies(), cookie_filename)
        return True
    else:
        __log("Login failure.")
        return False


def test_multiimage(
        path: str,
        getnewcaptcha: Callable = None,
        oncaptchasolve: Callable = None
        ) -> None:

    import glob
    imagelist = []

    for filename in glob.glob(path+'/*.png'):
        # im = Image.open(filename)
        with open(filename, 'rb') as image:
            f = image.read()
            b = bytearray(f)
            imagelist.append((filename, b))

    def getcapchtas():
        if len(imagelist) == 0:
            return []
        filename, image = imagelist.pop()
        cap = Captcha(filename, image, captype='img')
        return [cap]

    def oncaptchasolve(ans: str):
        print(f'captcha solved with ans {ans}')
    x, y = 6, 1

    startcap = []

    for i in range(x*y):
        startcap += getcapchtas()

    event = MulticaptchaGUI(startcap, oncaptchasolve, getcapchtas, x, y)

    event.start_event()


def runevent_new():
    user_settings_fp = 'user.settings'
    site_settings_fp = 'site.settings'
    buyer_settings_fp = 'buyer.settings'

    if SettingsFileMaker.needs_user_setup(
            user_settings_fp, site_settings_fp, buyer_settings_fp):
        print("Exiting. Please fill out settings files")
        quit()

    user_settings = UserSettings(filepath=user_settings_fp)
    site_settings = SiteSettings(filepath=site_settings_fp)
    rochandler = RocWebHandler(site_settings)

    if not login(rochandler, user_settings):
        print('Error logging in.')
        quit()

    event = SpyEvent(rochandler, user_filter, reversed_order)
    event.start_event()
    save_cookies_to_path(rochandler.get_cookies(), cookie_filename)


runevent_new()
