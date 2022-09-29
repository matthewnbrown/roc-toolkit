from collections import defaultdict, deque
from random import random
from time import time
from typing import Callable, Deque, Iterable, List
from threading import Thread, Lock

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
        self._captchamap = {}
        self._targetfilter = userfilter
        self._reversedordeer = reversedorder
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
        for user in new_users:
            if self._targetfilter(user):
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
                break

            newuser = self._userfilter(user_resp['result'])
            self._battlefield.extend(newuser)

        self._battlefield.reverse()
        self._bflock.release()

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
            captcha, targeturl, payload)

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

        self._gui.start()
