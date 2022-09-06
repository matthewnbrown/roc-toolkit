import html
import time
import unicodedata
from rocalert.roc_settings.settingstools import SettingsFileMaker, \
    SiteSettings, UserSettings
from rocalert.roc_web_handler import RocWebHandler
from rocalert.cookiehelper import load_cookies_from_path, \
    load_cookies_from_browser
from os.path import exists

targetids = [29428, 30066]
mingold = 1000000000
delay_ms = 500
cookie_filename = 'cookies'


def getgoldfrompage(page: str) -> int:
    index = page.index('playercard_gold c">')
    endindex = page[index:index+200].index(' Gold')
    goldstr = page[index + len('playercard_gold c">?')-1:index+endindex]
    if '?' in goldstr:
        return -1
    goldstr = html.unescape(goldstr).strip().replace(',', '')
    return int(goldstr)


def getgold(roc: RocWebHandler, id: str):
    url = roc.site_settings['roc_home'] + f'/stats.php?id={id}'
    roc.go_to_page(url)
    if roc.r.status_code != 200:
        return -1
    else:
        return getgoldfrompage(roc.r.text)


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

    res = roc.login(
        us.get_setting('email'),
        us.get_setting('password')
    )

    if res:
        __log("Login success.")
    else:
        __log("Login failure.")
        return False


def goldformat(gold: int) -> str:
    if gold == -1:
        return '???'
    return "{:,}".format(gold)


def attack(roc: RocWebHandler, id: str) -> bool:
    url = roc.site_settings['roc_home'] + f'/attack.php?id={id}'
    captcha = roc.get_url_img_captcha(url)
    
    return False


def run():
    user_settings_fp = 'user.settings'
    site_settings_fp = 'site.settings'
    buyer_settings_fp = 'buyer.settings'

    if SettingsFileMaker.needs_user_setup(
            user_settings_fp, site_settings_fp, buyer_settings_fp):
        print("Exiting. Please fill out settings files")
        quit()

    user_settings = UserSettings(filepath=user_settings_fp)
    sitesettings = SiteSettings(filepath=site_settings_fp)
    rochandler = RocWebHandler(sitesettings)

    for i in range(len(targetids)):
        targetids[i] = str(targetids[i])

    login(rochandler, user_settings)

    while True:
        for id in targetids:
            gold = getgold(rochandler, id)
            print(f'ID: {id} | Gold: {goldformat(gold)}')
            if gold > mingold:
                print('HIT')
            time.sleep(delay_ms/1000)
        print('-----------------------')


run()