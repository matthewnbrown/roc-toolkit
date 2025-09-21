from datetime import datetime
import html
import random
import threading
import time
from os.path import exists

from rocalert.cookiehelper import load_cookies_from_browser, load_cookies_from_path
from rocalert.captcha.captchaprovider import CaptchaProvider
from rocalert.roc_settings import SettingsSetupHelper, UserSettings
from rocalert.roc_web_handler import Captcha, RocWebHandler
from rocalert.services.captchaservices import ManualCaptchaSolverService
from rocalert.services.urlgenerator import ROCDecryptUrlGenerator
from rocalert.services.useragentgenerator import (
    Browser,
    OperatingSystem,
    UserAgentGenerator,
)

targetids = [29428]
use_captcha = False
mingold = 10_000_000_000  # 10b
delay_min_ms = 200
delay_max_ms = 300
beep = True


cookie_filename = "cookies"


def getgoldfrompage(page: str) -> int:
    index = page.index('playercard_gold c">')
    endindex = page[index : index + 200].index(" Gold")
    goldstr = page[index + len('playercard_gold c">?') - 1 : index + endindex]
    if "?" in goldstr:
        return -1
    goldstr = html.unescape(goldstr).strip().replace(",", "")
    return int(goldstr)


def getgold(roc: RocWebHandler, id: str):
    url = roc.url_generator.get_home() + f"stats.php?id={id}"
    roc.go_to_page(url)
    if roc.r.status_code != 200:
        return -1
    else:
        return getgoldfrompage(roc.r.text)


def __load_browser_cookies(roc: RocWebHandler, us: UserSettings) -> bool:
    if us.get_setting("load_cookies_from_browser").value:
        cookies = load_cookies_from_browser(
            us.get_setting("browser").value, roc.url_generator.get_home()
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
    __log("Logging in.")
    if __load_browser_cookies(roc, us) and roc.is_logged_in():
        __log(
            "Successfully pulled cookie from {}".format(us.get_setting("browser").value)
        )
        return True

    res = roc.login(us.get_setting("email").value, us.get_setting("password").value)

    if res:
        __log("Login success.")
    else:
        __log("Login failure.")
        return False


def goldformat(gold: int) -> str:
    if gold == -1:
        return "???"
    return "{:,}".format(gold)


def attack(roc: RocWebHandler, id: str, captchacache: CaptchaProvider) -> bool:
    start = datetime.now()
    
    if use_captcha:
        captcha = captchacache.get_solved_captcha()
        captcha_get_time = datetime.now() - start

        if captcha_get_time.total_seconds() > 1.5:
            print("took to long to get captcha.. resetting")
            return False
    else:
        captcha = None

    attack_url = roc.url_generator.get_attack(id)
    attack_page = roc.get_attack_page(id)

    print(f"Received answer: '{captcha.ans}'")
    if use_captcha and (captcha is None or int(captcha.ans) not in [1, 2, 3, 4, 5, 6, 7, 8, 9]):
        raise Exception("Bad captcha received from solver")

    post_captcha_gold = getgold(roc, id)

    if not is_target_valid(post_captcha_gold, id):
        print(f"Target {id} is no longer valid. Gold: {goldformat(post_captcha_gold)}")
        return False

    payload = {
        "defender_id": id,
        "mission_type": "attack",
        "attacks": attack_page.max_attack_turns,
    }
    return roc.submit_captcha_url(captcha, attack_url, payload, RocWebHandler.Pages.ATTACK)


def playbeep(freq: int = 700):
    try:
        import winsound

        winsound.Beep(freq, 2000)
    except ImportError:
        print("ERROR SETTING UP BEEPING!")


def get_randdelay(minms, maxms) -> float:
    range = maxms - minms
    waittime = minms + int(random.uniform(0, 1) * (range))
    return waittime / 1000


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


def is_target_valid(gold: int, id: str) -> bool:
    return gold >= mingold and id in targetids


def run():
    user_settings_fp = "user.settings"

    filepaths = {
        "user": ("user.settings", UserSettings),
    }

    settings_file_error = False

    for _, infotuple in filepaths.items():
        path, settingtype = infotuple
        if SettingsSetupHelper.needs_setup(path):
            settings_file_error = True
            SettingsSetupHelper.create_default_file(path, settingtype.DEFAULT_SETTINGS)
            print(f"Created settings file {path}.")

    if settings_file_error:
        print("Exiting. Please fill out settings files")
        quit()

    user_settings = UserSettings(filepath=user_settings_fp)
    url_generator = ROCDecryptUrlGenerator()
    rochandler = RocWebHandler(
        urlgenerator=url_generator, default_headers=_get_default_headers()
    )

    for i in range(len(targetids)):
        targetids[i] = str(targetids[i])

    login(rochandler, user_settings)
    time.sleep(1)
    print("Starting..")

    def captcha_provider():
        url = rochandler.url_generator.get_armory()
        captcha = None

        while (
            captcha is None
            or int(captcha.ans) not in [1, 2, 3, 4, 5, 6, 7, 8, 9]
            and not captcha.is_expired
        ):
            captcha = rochandler.get_url_img_captcha(url)

            if captcha.type and captcha.type == Captcha.CaptchaType.TEXT:
                print("Text captcha!!!")
                quit()

            mcs = ManualCaptchaSolverService()
            captcha = mcs.solve_captcha(captcha)
            print(f"got answer {captcha.ans}")

        return captcha

    if use_captcha:
        captchacache = CaptchaProvider(captcha_provider, cachesize=3)
        captchacache.start()
    else:
        captchacache = None

    while True:
        for id in targetids:
            gold = getgold(rochandler, id)
            print(f"ID: {id} | Gold: {goldformat(gold)}")
            if is_target_valid(gold, id):
                print("Target Found!")
                if beep:
                    thr = threading.Thread(target=playbeep, args=(1000,), kwargs={})
                    thr.start()

                hit = attack(rochandler, id, captchacache)
                if hit:
                    print("target hit... quitting!")
                    quit()
                else:
                    print("target hit failed")
            time.sleep(get_randdelay(delay_min_ms, delay_max_ms))
        print("-----------------------")


if beep:
    thr = threading.Thread(target=playbeep, args=(750,), kwargs={})
    thr.start()

run()
