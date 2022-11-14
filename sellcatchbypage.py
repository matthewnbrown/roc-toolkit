from rocalert.services.rocwebservices import \
    BattlefieldPageService, AttackService
from rocalert.roc_settings import SiteSettings, BuyerSettings,\
    UserSettings, SettingsSetupHelper
from rocalert.specialtools import BFSellCatch
from rocalert.roc_web_handler import RocWebHandler
from rocalert.rocpurchases import ROCBuyer
from rocalert.rocaccount import BattlefieldTarget
from rocalert.cookiehelper import load_cookies_from_path, \
    load_cookies_from_browser, save_cookies_to_path
import os


def _should_att(target: BattlefieldTarget):
    badranks = [112]
    badids = [7530]

    mingold = 2 * (10**9)  # 2 x (1 billion)

    return target.gold >= mingold\
        and int(target.id) not in badids \
        and target.rank not in badranks


def login(roc: RocWebHandler, us: UserSettings, cookie_filename='cookies'):
    print('Logging in.')
    if __load_cookies_file(roc, cookie_filename) and roc.is_logged_in():
        print('Successfully used cookie file')
        return True

    if __load_browser_cookies(roc, us) and roc.is_logged_in():
        print('Successfully pulled cookie from {}'.format(
            us.get_setting('browser').value))
        save_cookies_to_path(roc.get_cookies(), cookie_filename)
        return True

    roc.login(
        us.get_setting('email'),
        us.get_setting('password')
    )

    if roc.is_logged_in():
        print("Login success.")
        save_cookies_to_path(roc.get_cookies(), cookie_filename)
        return True
    else:
        print("Login failure.")
        return False


def __load_browser_cookies(roc: RocWebHandler, us: UserSettings) -> bool:
    if us.get_setting('load_cookies_from_browser'):
        cookies = load_cookies_from_browser(
            us.get_setting('browser').value,
            roc.site_settings.get_home()
            )
        roc.add_cookies(cookies)
        return True
    return False


def __load_cookies_file(roc: RocWebHandler, cookie_filename: str) -> bool:
    if os.path.exists(cookie_filename):
        print("Loading saved cookies")
        cookies = load_cookies_from_path(cookie_filename)
        if cookies is not None:
            roc.add_cookies(cookies)


if __name__ == '__main__':

    filepaths = {
        'user': ('user.settings', UserSettings),
        'site': ('site.settings', SiteSettings),
        'buyer': ('buyer.settings', BuyerSettings),
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
        quit()

    user_settings = UserSettings(filepath=filepaths['user'][0])
    site_settings = SiteSettings(filepath=filepaths['site'][0])
    buyer_settings = BuyerSettings(filepath=filepaths['buyer'][0])
    rochandler = RocWebHandler(site_settings)

    if not login(rochandler, user_settings):
        print('Error logging in.')
        quit()

    ps = BattlefieldPageService()
    atts = AttackService()

    buyer = ROCBuyer(rochandler, buyer_settings)

    sellcatch = BFSellCatch(ps, atts, buyer, rochandler)
    sellcatch.run(_should_att, 0.05)
