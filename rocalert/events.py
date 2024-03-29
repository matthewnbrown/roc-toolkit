from collections import defaultdict, deque
import io
import random
import time
import numpy as np
import PIL.Image
from typing import Callable, Deque, Iterable, List
from threading import Thread, Lock, Event
from rocalert.captcha.captcha_logger import CaptchaLogger

from rocalert.captcha.equation_solver import EquationSolver
from rocalert.roc_web_handler import Captcha, RocWebHandler
from rocalert.rocaccount import BattlefieldTarget
from rocalert.captcha.solvers.multicaptchaguisolver import MulticaptchaGUI
from rocalert.services.rocwebservices import BattlefieldPageService
from rocalert.services.urlgenerator import ROCDecryptUrlGenerator


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
            reversedorder: bool = True,
            captcha_save_path: str = None,
            captchalogger: CaptchaLogger = None
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
        self._captchalogger = captchalogger
        self._captcha_save_path = captcha_save_path
        self._roc = roc
        self._targetfilter = userfilter
        self._reversedorder = reversedorder
        self._usercaptchas = defaultdict(set)
        self._spystatus = defaultdict(self.SpyStatus)
        self._battlefield = None

        self._updatecaptchaslock = Lock()
        self._captchaslock = Lock()
        self._roclock = Lock()
        self._newcaptchas = Event()
        self._captchas = deque()

        self._guiexit = False

        self._urlgenerator = ROCDecryptUrlGenerator()

    def _save_captcha(self, captcha: Captcha) -> None:
        if self._captcha_save_path is None:
            return

        img = PIL.Image.open(io.BytesIO(captcha.img))
        path = self._captcha_save_path + captcha.hash + '.png'
        img.save(path)

    def _log_captcha(self, captcha: Captcha) -> None:
        if self._captchalogger is None:
            return
        self._captchalogger.log_captcha(captcha)

    def _hit_spy_limit(self, responsetext: str) -> bool:
        return 'You cannot recon this person' in responsetext

    def _get_spy_url(self, user: BattlefieldTarget) -> str:
        return self._urlgenerator.get_home() \
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
        self._roclock.acquire()
        cap = self._roc.get_img_captcha('roc_armory')
        self._roclock.release()
        return cap

    def _check_captcha_is_noimage(self, captcha: Captcha) -> bool:
        nparr = np.frombuffer(captcha.img, dtype=np.uint8)
        mean = np.mean(nparr)
        return mean < 110

    def _getnewcaptchas(self, num_captchas: int) -> List[Captcha]:
        result = []
        consfailures = 0
        while num_captchas > 0:
            if consfailures > 3:
                return result

            self._roclock.acquire()
            captype = self._roc.get_page_captcha_type(
                self._urlgenerator.get_armory())
            self._roclock.release()

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

            self._save_captcha(cap)
            if self._check_captcha_is_noimage(cap):
                print('Rejected no image captcha')
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

        self._roclock.acquire()
        valid_captcha = self._roc.submit_captcha_url(
            captcha, targeturl, payload)

        text = self._roc.r.text
        self._roclock.release()

        captcha.ans_correct = valid_captcha
        if not valid_captcha:
            return 'error'
        if self._hit_spy_limit(text):
            return 'maxed'
        elif self._detect_admin(text):
            return 'admin'

        return 'success'

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

    def _get_captcha_buffersize(self) -> int:
        self._captchaslock.acquire()
        buffersize = len(self._captchas)
        self._captchaslock.release()
        return buffersize

    def _signalfinish(self) -> None:
        self._guiexit = True
        self._captchaslock.acquire()
        self._captchas.append(Captcha(''))
        self._captchaslock.release()
        self._newcaptchas.set()

    def _captcha_delay(self) -> None:
        time.sleep(max(0.4 + random.gauss(.4, .1), .35))

    def _nextuser_delay(self) -> None:
        time.sleep(max(1.5 + random.gauss(.5, .3), 1))

    def _purge_expired_captchas(self) -> None:
        print('Detected expired captchas, purging...')

        count = 1

        self._captchaslock.acquire()
        while len(self._captchas) > 0 and self._captchas[0].is_expired:
            count += 1
            self._captchas.popleft()
        self._captchaslock.release()

        print(f'Purged {count} captcha{"" if count == 1 else "s"}')

    def _handle_spying(self) -> None:
        last_user_skipped = False

        while len(self._battlefield) > 0:
            user = self._battlefield.popleft()
            if not last_user_skipped:
                self._nextuser_delay()
            last_user_skipped = False
            cons_fails = 0

            count = 0
            while count < 10:
                if cons_fails > 3:
                    print('Failed too many times, skipping user '
                          + f'#{user.rank}: {user.name}')

                captcha = self._pull_next_captcha()

                if self._guiexit:
                    return
                if captcha.is_expired:
                    self._purge_expired_captchas()
                    continue

                spyres = self._spyuser(user, captcha)
                self._log_captcha(captcha)

                if spyres == 'error':
                    cons_fails += 1
                else:
                    cons_fails = 0

                if spyres == 'success':
                    count += 1
                elif spyres == 'admin':
                    print(f'Detected untouchable admin account {user.name}.')
                    last_user_skipped = True
                    break
                elif spyres == 'maxed':
                    last_user_skipped = True
                    break

                self._captcha_delay()

            buffersize = self._get_captcha_buffersize()
            print(f'Finished spying user #{user.rank}: {user.name}. '
                  + f'Buffer size: {buffersize}')

        print('Battlefield has been cleared')

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
            if not self._guiexit:
                print('Event finished')
                self._gui.signal_end()
            else:
                print('Detected clicker terminated, exiting.')

        xcount, ycount = 8, 1
        initcaptchas = self._getnewcaptchas(xcount*ycount*2)

        self._gui = MulticaptchaGUI(
            initcaptchas, onsolvecallback, getnewcaptchas, xcount, ycount)

        spyhandle = Thread(target=eventthread)
        spyhandle.start()
        self._gui.start()
        self._signalfinish()
        spyhandle.join()
