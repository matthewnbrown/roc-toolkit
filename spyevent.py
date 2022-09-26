from collections import defaultdict, deque
from random import random
from time import time
from typing import Callable, Deque, Iterable, List, Set
from os.path import exists
from threading import Thread, Lock


from rocalert.captcha.equation_solver import EquationSolver

from rocalert.roc_settings.settingstools import SettingsFileMaker, \
    SiteSettings, UserSettings
from rocalert.roc_web_handler import Captcha, RocWebHandler
from rocalert.rocaccount import BattlefieldTarget
from rocalert.cookiehelper import load_cookies_from_path, \
    load_cookies_from_browser, save_cookies_to_path
from rocalert.services.captchaservices import MulticaptchaGUI
from rocalert.services.rocwebservices import BattlefieldPageService

# Comma separated ids. Put your own ID in here
starting_rank = 1
skip_ids = {7530, 27607, 31123}
skip_ranks = {112}
# This will only spy on selected IDs. Skip_ids will be ignored
onlyspy_ids = {}

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
        save_cookies_to_path(roc.get_cookies(), cookie_filename)
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
        save_cookies_to_path(roc.get_cookies(), cookie_filename)
        return True
    else:
        __log("Login failure.")
        return False


def SolveEqn(roc: RocWebHandler):
    c = roc.get_equation_captcha()
    print(f'Received equation \'{c.hash}\'')
    c.ans = EquationSolver.solve_equation(c.hash)

    minsleeptime = 3 if int(c.ans) % 10 == 0 else 5
    time.sleep(minsleeptime + int(random.uniform(0, 1) * minsleeptime))

    roc.submit_equation(c)


class SpyEvent:
    class SpyStatus:
        def __init__(self) -> None:
            self.active_captchas = 0
            self.solved_captchas = 0

        @property
        def required_captchas(self):
            return max(10 - self.solved_captchas - self.active_captchas, 0)

    # TODO: Change all the user filters to one Callable filter
    def __init__(
            self,
            roc: RocWebHandler,
            start_rank: int = 1,
            skiplist: Set[str] = set(),
            onlyspylist: Set[str] = set(),
            skip_rank: Set[int] = set()
            ) -> None:
        """_summary_

        Args:
            roc (RocWebHandler): _description_
                ROC session to use for spy event
            skiplist (Set[str], optional): _description_. Default: Set().
                List of user IDs to not spy
            onlyspylist (Set[str], optional): _description_. Default: Set().
                List of user IDs that will only be spied on.
                All other users will be skipped if this
                parameter is not None or an empty list
        """
        self._roc = roc
        self._skiplist = skiplist
        self._onlyspylist = onlyspylist
        self._start_rank = start_rank,
        self._skip_rank = skip_rank
        self._restrictedtargets = onlyspylist and len(onlyspylist) > 0
        self._captchamap = {}
        self._usercaptchas = defaultdict(set)
        self._spystatus = defaultdict(self.SpyStatus)
        self._bflock = Lock()
        self._battlefield = None
        self._captchamaplock = Lock()
        self._updating_captchas = False

    def _hit_spy_limit(self, responsetext: str) -> bool:
        return 'You cannot recon this person' in responsetext

    def _get_captcha(self, user: BattlefieldTarget) -> Captcha:
        url = self._get_spy_url(user)
        captcha = self._roc.get_url_img_captcha(url)
        return captcha

    def _get_spy_url(self, user: BattlefieldTarget) -> str:
        return self._roc.site_settings['roc_home'] \
            + f'/attack.php?id={user.id}&mission_type=recon'

    def _userfilter(
            self,
            new_users: Iterable[BattlefieldTarget]
            ) -> Deque[BattlefieldTarget]:
        res = deque()
        if self._onlyspylist and len(self._onlyspylist) > 0:
            for user in new_users:
                if user.id in self._onlyspylist:
                    res.append(user)
            return res

        for user in new_users:
            if (user.id not in self._skiplist
                    and int(user.rank) not in self._skip_rank
                    and int(user.rank) >= starting_rank):
                res.append(user)
        return res

    def _get_all_users(self) -> None:
        self._bflock.acquire()
        pagenum = 1
        self._battlefield = self._battlefield if self._battlefield else deque()

        while True:
            user_resp = BattlefieldPageService.run_service(self._roc, pagenum)
            pagenum += 1
            if user_resp['response'] == 'error':
                self._bflock.release()
                return

            newuser = self._userfilter(user_resp['result'])
            self._battlefield.extend(newuser)

    def _remove_user(self, user: BattlefieldTarget) -> None:
        print(f'{user.name} was removed from the list')
        for captcha in self._usercaptchas[user]:
            del self._captchamap[captcha]

        self._spystatus[user].active_captchas = 0
        self._spystatus[user].solved_captchas = 10

        self._gui.remove_captchas(self._usercaptchas[user])
        del self._usercaptchas[user]

    def _handle_maxed_target(self, user: BattlefieldTarget) -> None:
        print(f'Maxed out spy attempts on {user.name}')
        self._remove_user(user)

    def _handle_admin(self, user: BattlefieldTarget) -> None:
        print(f'Detected admin account {user.name}.')
        self._remove_user(user)

    def _detect_admin(self, responsetext: str) -> bool:
        return 'Administrator account' in responsetext

    def _getnewcaptchas(self, num_captchas: int) -> List[Captcha]:
        backup = []
        result = []
        self._bflock.acquire()

        while num_captchas > 0 and len(self._battlefield) > 0:
            cur_user = self._battlefield.popleft()
            backup.append(cur_user)
            count = self._spystatus[cur_user].required_captchas

            getcaps = min(num_captchas, count)
            num_captchas -= getcaps
            consfailures = 0
            for i in range(getcaps):
                if consfailures > 2:
                    print(f"Too many failures, skipping {cur_user.name}")
                    break

                captype = self._roc.get_page_captcha_type(
                        self._get_spy_url(cur_user))
                if captype == Captcha.CaptchaType.EQUATION:
                    print('Warning: received equation captcha')
                    SolveEqn(self._roc)
                    i -= 1
                    consfailures += 1

                if captype == Captcha.CaptchaType.TEXT:
                    print("Warning: Received TEXT Captcha"
                          + ' attempting captcha reset')
                    self._roc.reset_cooldown()
                    i -= 1
                    consfailures += 1
                    continue

                cap = self._get_captcha(cur_user)
                if cap is None or cap.hash is None:
                    i -= 1
                    print(f'Failed getting captcha for {cur_user.name}')
                    consfailures += 1
                    continue

                self._captchamaplock.acquire()
                self._captchamap[cap] = cur_user
                self._usercaptchas[cur_user].add(cap)
                self._spystatus[cur_user].active_captchas += 1
                self._captchamaplock.release()
                consfailures = 0
                result.append(cap)

        while len(backup) > 0:
            self._battlefield.appendleft(backup.pop())
        self._bflock.release()
        return result

    def _send_captchas_to_gui(self, captchas: List[Captcha]) -> None:
        self._gui.add_captchas(captchas)

    def _getsend_captchas(self, count) -> None:
        self._captchamaplock.acquire()
        updating = self._updating_captchas

        if not updating:
            self._updating_captchas = True
        self._captchamaplock.release()

        if not updating:
            caps = self._getnewcaptchas(count)
            self._send_captchas_to_gui(caps)
            self._captchamaplock.acquire()
            self._updating_captchas = False
            self._captchamaplock.release()

    def _oncaptchasolved(self, captcha: Captcha) -> None:
        self._captchamaplock.acquire()
        # TODO: Add specific thread that constantly handles solved captchas
        if captcha not in self._captchamap:
            self._captchamaplock.release()
            return

        user = self._captchamap[captcha]

        targeturl = self._get_spy_url(user)

        payload = {
            'defender_id': user.id,
            'mission_type': 'recon',
            'reconspies': 1
        }

        valid_captcha = self._roc.submit_captcha_url(
            captcha, targeturl, payload, 'roc_spy')

        del self._captchamap[captcha]
        self._usercaptchas[user].remove(captcha)
        self._spystatus[user].active_captchas -= 1
        if valid_captcha:
            self._spystatus[user].solved_captchas += 1
        if self._hit_spy_limit(self._roc.r.text):
            self._handle_maxed_target(user)
        elif self._detect_admin(self._roc.r.text):
            self._handle_admin(user)
        self._captchamaplock.release()

    def start_event(self) -> None:
        if not self._roc.is_logged_in():
            print('Error: Could not start event. ROC is not logged in')
            return

        self._get_all_users()

        if len(self._battlefield) == 0:
            print("Error: could not get battlefield")
            return
        else:
            print(f"Detected {len(self._battlefield)} users.")

        def onsolvecallback(captcha: Captcha) -> Thread:
            t = Thread(target=self._oncaptchasolved, args=[captcha])
            t.start()
            return t

        def getnewcaptchas(desiredcount) -> Thread:
            t = Thread(target=self._getsend_captchas, args=[desiredcount])
            t.start()
            return t

        xcount, ycount = 4, 1
        initcaptchas = self._getnewcaptchas(xcount*ycount*2)

        self._gui = MulticaptchaGUI(
            initcaptchas, onsolvecallback, getnewcaptchas, xcount, ycount)
        self._running = True

        self._gui.start_event()


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

    skip_idsstr = {str(id) for id in skip_ids}
    onlyspy_idsstr = {str(id) for id in onlyspy_ids}
    event = SpyEvent(rochandler, starting_rank,
                     skip_idsstr, onlyspy_idsstr, skip_ranks)
    event.start_event()


runevent_new()
