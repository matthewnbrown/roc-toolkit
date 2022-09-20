from rocalert.roc_settings.settingstools import SettingsFileMaker, \
    SiteSettings, UserSettings
from rocalert.roc_web_handler import RocWebHandler
from rocalert.services.manualcaptchaservice import ManualCaptchaService
from rocalert.cookiehelper import load_cookies_from_path, \
    load_cookies_from_browser
from os.path import exists

from rocalert.services.rocwebservices import BattlefieldPageService

skip_ids = {31123}

delay_ms = 100
cookie_filename = 'cookies'


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
    if __load_browser_cookies(roc, us) and roc.is_logged_in():
        __log('Successfully pulled cookie from {}'.format(
            us.get_setting('browser')))
        return True

    if __load_cookies_file(roc, cookie_filename) and roc.is_logged_in():
        __log('Successfully used cookie file')
        return True

    roc.login(
        us.get_setting('email'),
        us.get_setting('password')
    )

    if roc.is_logged_in():
        __log("Login success.")
    else:
        __log("Login failure.")
        return False


def spyevent(
    rochandler: RocWebHandler,
    user_settings: UserSettings,
        ) -> None:

    if not login(rochandler, user_settings):
        print('Error logging in.')
        quit()

    i = 1
    while True:
        userlist = BattlefieldPageService.run_service(rochandler, i)
        i += 1
        if userlist['response'] == 'error':
            print('Finished.')
            break

        for user in userlist['result']:
            print(f'Current target: {user.name}')
            if int(user.id) in skip_ids:
                print('Skipping user')
                continue

            for i in range(10):
                spyuser(rochandler, user.id)



def spyuser(roc: RocWebHandler, userid: str) -> bool:
    targeturl = roc.site_settings['roc_home'] \
        + f'/attack.php?id={userid}&mission_type=recon'
    captcha = roc.get_url_img_captcha(targeturl)
    if captcha is None:
        return False

    captchares = ManualCaptchaService().run_service(
        roc, None, {'captcha': captcha})

    validans = {str(i) for i in range(1, 10)}
    if 'error' in captchares or captchares['captcha'].ans not in validans:
        return False

    payload = {
        'defender_id': userid,
        'mission_type': 'recon',
        'reconspies': 1
    }

    return roc.submit_captcha_url(captcha, targeturl, payload, 'roc_spy')


def runevent():
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

    spyevent(rochandler, user_settings)

runevent()
