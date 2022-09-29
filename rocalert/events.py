from collections import defaultdict, deque
import random
import time
from typing import Callable, Deque, Iterable, List
from threading import Thread, Lock, Event

from rocalert.captcha.equation_solver import EquationSolver
from rocalert.roc_web_handler import Captcha, RocWebHandler
from rocalert.rocaccount import BattlefieldTarget
from rocalert.services.captchaservices import MulticaptchaGUI
from rocalert.services.rocwebservices import BattlefieldPageService


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
            userfilter: Callable,
            reversedorder: bool = True
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
        self._targetfilter = userfilter
        self._reversedorder = reversedorder
        self._usercaptchas = defaultdict(set)
        self._spystatus = defaultdict(self.SpyStatus)
        self._battlefield = None

        self._updatecaptchaslock = Lock()
        self._captchaslock = Lock()
        self._newcaptchas = Event()
        self._captchas = deque()

    def _hit_spy_limit(self, responsetext: str) -> bool:
        return 'You cannot recon this person' in responsetext

    def _get_spy_url(self, user: BattlefieldTarget) -> str:
        return self._roc.site_settings['roc_home'] \
            + f'/attack.php?id={user.id}&mission_type=recon'

    def _filterusers(
            self,
            new_users: Iterable[BattlefieldTarget]
            ) -> Deque[BattlefieldTarget]:
        res = deque()
        for user in new_users:
            if self._targetfilter(user):
                res.append(user)
        return res

    def _get_all_users(self) -> None:
        pagenum = 1
        self._battlefield = self._battlefield if self._battlefield else deque()

        while True:
            user_resp = BattlefieldPageService.run_service(self._roc, pagenum)
            pagenum += 1
            if user_resp['response'] == 'error':
                break

            newuser = self._filterusers(user_resp['result'])
            self._battlefield.extend(newuser)

        if self._reversedorder:
            self._battlefield.reverse()

    def _detect_admin(self, responsetext: str) -> bool:
        return 'Administrator account' in responsetext

    def _getcaptcha(self) -> Captcha:
        return self._roc.get_img_captcha('roc_armory')

    def _getnewcaptchas(self, num_captchas: int) -> List[Captcha]:
        result = []
        consfailures = 0
        while num_captchas > 0:
            if consfailures > 3:
                return result

            captype = self._roc.get_page_captcha_type(
                self._roc.site_settings['roc_armory'])

            if captype == Captcha.CaptchaType.EQUATION:
                print('Warning: received equation captcha')
                SolveEqn(self._roc)
                consfailures += 1
                continue
            if captype == Captcha.CaptchaType.TEXT:
                print("Warning: Received TEXT Captcha"
                      + ' attempting captcha reset')
                self._roc.reset_cooldown()
                consfailures += 1
                continue

            cap = self._getcaptcha()
            if cap is None or cap.hash is None:
                consfailures += 1
                continue

            consfailures = 0
            num_captchas -= 1
            result.append(cap)
        return result

    def _send_captchas_to_gui(self, captchas: List[Captcha]) -> None:
        self._gui.add_captchas(captchas)

    def _getsend_captchas(self, count) -> None:
        if not self._updatecaptchaslock.locked():
            self._updatecaptchaslock.acquire()
            caps = self._getnewcaptchas(count)
            self._send_captchas_to_gui(caps)
            self._updatecaptchaslock.release()

    def _oncaptchasolved(self, captcha: Captcha) -> None:
        if captcha and captcha.ans:
            self._captchaslock.acquire()
            self._captchas.append(captcha)
            self._newcaptchas.set()
            self._captchaslock.release()

    def _spyuser(self, user: BattlefieldTarget, captcha: Captcha) -> str:
        targeturl = self._get_spy_url(user)
        payload = {
            'defender_id': user.id,
            'mission_type': 'recon',
            'reconspies': 1
        }

        valid_captcha = self._roc.submit_captcha_url(
            captcha, targeturl, payload)

        if not valid_captcha:
            return 'error'
        if self._hit_spy_limit(self._roc.r.text):
            'maxed'
        elif self._detect_admin(self._roc.r.text):
            'admin'

    def _pull_next_captcha(self) -> Captcha:
        self._captchaslock.acquire()
        self._newcaptchas.clear()
        if len(self._captchas) > 0:
            cap = self._captchas.popleft()
        else:
            self._captchaslock.release()
            self._newcaptchas.wait()
            self._captchaslock.acquire()
            cap = self._captchas.popleft()
            self._newcaptchas.clear()
        self._captchaslock.release()

        return cap

    def _handle_spying(self) -> None:
        while len(self._battlefield) > 0:
            user = self._battlefield.popleft()
            cons_fails = 0

            count = 0
            while count < 10:
                if cons_fails > 3:
                    print('Failed too many times, skipping user')
                captcha = self._pull_next_captcha()
                spyres = self._spyuser(user, captcha)

                if spyres == 'success':
                    count += 1
                    cons_fails = 0
                if spyres == 'admin':
                    print(f'Detected untouchable admin account {user.name}.')
                    break
                elif spyres == 'maxed':
                    break
                elif spyres == 'error':
                    cons_fails += 1

            print(f'Finished spying user #{user.rank}: {user.name}')

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

        def eventthread():
            self._handle_spying()
            self._gui.end()

        xcount, ycount = 4, 1
        initcaptchas = self._getnewcaptchas(xcount*ycount*2)

        self._gui = MulticaptchaGUI(
            initcaptchas, onsolvecallback, getnewcaptchas, xcount, ycount)

        spyhandle = Thread(target=eventthread)
        spyhandle.start()
        self._gui.start()

        spyhandle.join()
