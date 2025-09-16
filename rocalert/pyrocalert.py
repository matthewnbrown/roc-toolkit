from .captcha.equation_solver import EquationSolver
from .services.remote_lookup import RemoteCaptcha
from .services.captchaservices import CaptchaSolverServiceABC,\
    CaptchaReportException, CaptchaSolveException
from .rocpurchases import ROCBuyer, ROCTrainerABC
from .roc_settings import UserSettings
from .roc_web_handler import RocWebHandler
from .roc_web_handler import Captcha
from .captcha.captcha_logger import CaptchaLogger
from .cookiehelper import save_cookies_to_path, \
    load_cookies_from_path, load_cookies_from_browser

import rocalert.pages as pages
import bs4
import io
import PIL.Image
import time
import datetime
import random
from os.path import exists


class RocAlert:
    def __init__(self,
                 rochandler: RocWebHandler = None,
                 usersettings: UserSettings = None,
                 buyer: ROCBuyer = None,
                 trainer: ROCTrainerABC = None,
                 correctLog: CaptchaLogger = None,
                 generalLog: CaptchaLogger = None,
                 remoteCaptcha: RemoteCaptcha = None,
                 capsolver: CaptchaSolverServiceABC = None,
                 ) -> None:
        if rochandler is None:
            raise Exception("An existing ROC Handler must be passed!")
        self.roc = rochandler
        self.buyer = buyer
        self._trainer = trainer
        self.user_settings = usersettings.get_settings_old()
        self.validans = {str(i) for i in range(1, 10)}
        self.general_log = generalLog
        self.correct_log = correctLog
        self.__in_nightmode = False
        self.__last_login_time = None
        self.__last_purchase_time = None
        self.__last_train_time = None
        self.__purchase_error = False
        self.__training_error = False
        self.__failure_timeout = False
        self.__cooldown = False
        self._capsolver = capsolver

        self.cookie_filename = 'cookies'
        self.__useRemoteCatcha = True
        self.__remoteCaptcha = remoteCaptcha

    def __log(self, message: str, end=None, timestamp=True) -> None:
        if timestamp:
            ts = datetime.datetime.now().strftime("%H:%M:%S")
            print('{}: {}'.format(ts, message), end=end)
        else:
            print(message, end=end)

    def __get_waittime(self) -> int:
        inNightMode = self.__check_nightmode()
        if not inNightMode:
            min = self.user_settings['min_checktime_secs']
            max = self.user_settings['max_checktime_secs']
        else:
            # TODO: Modify so user doesn't sleep way past nightmode wake time
            min = self.user_settings['nightmode_minwait_mins'] * 60
            max = self.user_settings['nightmode_maxwait_mins'] * 60

        if min > max:
            min, max = max, min

        return min + int(random.uniform(0, 1) * (max - min))

    def __get_img_captcha_ans(self, captcha: Captcha) -> str:
        self.__save_captcha(captcha)

        if self.__useRemoteCatcha:
            res = self.__remoteCaptcha.lookup_remote(captcha)
            if res is not None and len(res) > 0:
                self.__log(f'Received result from remote: {res}')
                res = res.split(':', 1)
                if len(res) == 2:
                    captcha.ans = res[1]
                    return captcha.ans
        try:
            self._capsolver.solve_captcha(captcha)
        except CaptchaSolveException as e:
            self.__log(f'Exception solving captcha: {e}')
            captcha.ans = f'Exception: {e}'

        return captcha.ans

    def __save_captcha(self, captcha: Captcha):
        img = PIL.Image.open(io.BytesIO(captcha.img))
        path = self.user_settings['captcha_save_path'] + captcha.hash + '.png'
        img.save(path)
        return path

    def __log_general(self, captcha: Captcha):
        if self.general_log is not None:
            self.general_log.log_captcha(captcha)

    def __log_correct(self, captcha: Captcha):
        if self.correct_log is not None:
            self.correct_log.log_captcha(captcha=captcha)

    def __check_nightmode(self) -> bool:
        if not self.user_settings['enable_nightmode']:
            return False
        start = self.user_settings['nightmode_begin']
        end = self.user_settings['nightmode_end']
        now = datetime.datetime.now().time()

        if start <= end:
            innightmode = start <= now <= end
        else:
            innightmode = start <= now or now <= end

        if innightmode != self.__in_nightmode:
            self.__in_nightmode = innightmode

            if innightmode:
                self.__log('Entering nightmode.')
            else:
                self.__log('Exiting nightmode.')

        return innightmode

    def __sleep(self) -> None:
        waitTime = self.__get_waittime()
        save_cookies_to_path(self.roc.get_cookies(), self.cookie_filename)
        endtime = datetime.datetime.now() + datetime.timedelta(0, waitTime)
        self.__log('Taking a nap. Waking up at {}.'.format(
            endtime.strftime('%H:%M:%S')))
        try:
            time.sleep(waitTime)
        except KeyboardInterrupt:
            self.__log("Sleep interrupted by user. Exiting...")
            raise

    def __attempt_login(self) -> bool:
        self.__log('Session timed out. ', end='')
        if self.__load_browser_cookies() and self.roc.is_logged_in():
            self.__log('Successfully pulled cookie from {}'.format(
                    self.user_settings['browser']),
                timestamp=False
                )
            return True

        curtime = datetime.datetime.now()
        if self.__last_login_time:
            min_bugged_time = datetime.timedelta(0, 600)
            if curtime - self.__last_login_time <= min_bugged_time:
                self.consecutive_bugged_logins += 1
                time.sleep(3 + int(random.uniform(0, 1) * 5))
            else:
                self.consecutive_bugged_logins = 0

        self.__last_login_time = curtime
        res = self.roc.login(
            self.user_settings['email'],
            self.user_settings['password']
            )

        if res:
            self.consecutive_login_failures = 0
            self.__log("Login success.", timestamp=False)
            save_cookies_to_path(self.roc.get_cookies(), self.cookie_filename)
        else:
            self.consecutive_login_failures += 1
            self.__log("Login failure.", timestamp=False)
            return False

    def __captcha_final(self, captcha: Captcha) -> None:
        if captcha is None or captcha.img is None:
            return

        if 'ERROR' not in captcha.ans:
            try:
                self._capsolver.report_captcha(captcha)
            except CaptchaReportException as e:
                self.__log(f'Error reporting captcha: {e}')

        if captcha.ans_correct:
            self.__log_correct(captcha)
        if captcha.ans_correct and self.__useRemoteCatcha:
            self.__remoteCaptcha.add_remote(captcha)

        self.__log_general(captcha)

    def __handle_img_captcha(self, page: str, payload: dict = None) -> Captcha:
        captcha = self.roc.get_img_captcha(page)

        if captcha is None:
            return None
        if captcha.type and captcha.type == Captcha.CaptchaType.TEXT:
            captcha.ans_correct = False
            return captcha

        self.__get_img_captcha_ans(captcha)
        captcha.ans_correct = False
        ans = captcha.ans
        if len(ans) != 1 or ans not in self.validans:
            self.__log(("Warning: received response \'{}\' "
                        + "from captcha solver!").format(ans))
            if 'bad response: 503' in ans \
                    or ('exception' in ans.lower() and 'SOLVABLE' not in ans):
                waittime = 5 * (1 + self.consecutive_answer_errors**2)
                self.__log(
                    f"Waiting {waittime} seconds before attempting again..."
                    )
                time.sleep(waittime)
                captcha = None
            self.consecutive_answer_errors += 1
            return captcha
        else:
            self.__log('Received answer: \'{}\': '.format(ans), end='')

        self.consecutive_answer_errors = 0
        correct = self.roc.submit_captcha(captcha, ans, page, payload)
        if correct:
            self.__log("Correct answer", timestamp=False)
            self.consecutive_captcha_failures = 0
            captcha.ans_correct = True
        else:
            self.__log("Incorrect answer", timestamp=False)
            self.consecutive_captcha_failures += 1
        return captcha

    def __handle_equation_captcha(self) -> Captcha:
        c = self.roc.get_equation_captcha()
        self.__log(f'Received equation \'{c.hash}\'')
        c.ans = EquationSolver.solve_equation(c.hash)

        minsleeptime = 3 if int(c.ans) % 10 == 0 else 5
        time.sleep(minsleeptime + int(random.uniform(0, 1) * minsleeptime))

        c.ans_correct = self.roc.submit_equation(c)

        if c.ans_correct:
            self.__log(f"{c.hash} = {c.ans}")
            self.consecutive_captcha_failures = 0
        else:
            self.__log(f"{c.hash} != {c.ans}... oops")
            self.consecutive_captcha_failures += 1
        return c

    def __handle_captcha(self, captchaType: str) -> Captcha:
        self.__log(f'Detected {captchaType} captcha...')

        if captchaType == Captcha.CaptchaType.IMAGE:
            return self.__handle_img_captcha('roc_recruit')
        elif captchaType == Captcha.CaptchaType.EQUATION:
            return self.__handle_equation_captcha()

        return None

    def __init_cookie_loading(self) -> None:
        if self.__load_browser_cookies() and self.roc.is_logged_in():
            self.__log("Took login cookie from browser.")
        else:
            self.__load_cookies_file()

    def __check_failure_conditions(self) -> list[str]:
        failures = []
        max_clf = self.user_settings['max_consecutive_login_failures']
        max_caa = self.user_settings['max_consecutive_answer_errors']
        max_ccf = self.user_settings['max_consecutive_captcha_attempts']
        max_cbl = 4
        max_fpa = 5
        max_fta = 5
        max_cdclears = 2
        if self.consecutive_login_failures >= max_clf:
            failure_msg = f"Multiple login failures ({self.consecutive_login_failures}/{max_clf})"
            self.__log(f"ERROR: {failure_msg}")
            failures.append(failure_msg)
        if self.consecutive_answer_errors >= max_caa:
            failure_msg = f"Too many consecutive bad answers received ({self.consecutive_answer_errors}/{max_caa})!"
            self.__log(failure_msg)
            if self.user_settings['captcha_failure_timeout'] > 0:
                self.consecutive_answer_errors = 0
                self.__failure_timeout = True
            else:
                failures.append(failure_msg)
        if self.consecutive_captcha_failures >= max_ccf:
            failure_msg = f"Failed too many captchas ({self.consecutive_captcha_failures}/{max_ccf})!"
            self.__log(failure_msg)
            if self.user_settings['captcha_failure_timeout'] > 0:
                self.consecutive_captcha_failures = 0
                self.__failure_timeout = True
            else:
                failures.append(failure_msg)
        if self.consecutive_bugged_logins >= max_cbl:
            failure_msg = f"Too many logins in a very short period ({self.consecutive_bugged_logins}/{max_cbl})!"
            self.__log(f'Error: {failure_msg}')
            failures.append(failure_msg)
        if self.consecutive_purchase_attempts >= max_fpa:
            self.consecutive_purchase_attempts = 0
            failure_msg = f"Too many failed purchase attempts ({self.consecutive_purchase_attempts}/{max_fpa})! No longer attempting to purchase."
            self.__log(f'Error: {failure_msg}')
            self.__purchase_error = True
        if self.consecutive_training_attempts >= max_fta:
            self.consecutive_training_attempts = 0
            failure_msg = f"Too many failed training attempts ({self.consecutive_training_attempts}/{max_fta})! No longer attempting to train."
            self.__log(f'Error: {failure_msg}')
            self.__training_error = True
        if self.consecutive_cooldowns >= max_cdclears:
            self.consecutive_cooldowns = 0
            failure_msg = f"Text captcha failed to clear too many times ({self.consecutive_cooldowns}/{max_cdclears})."
            self.__log(failure_msg)
            self.__failure_timeout = True
        return failures

    def __check_buy_needed(self) -> bool:
        if self.buyer is None:
            return False
        if self.__purchase_error:
            self.__log('Not purchasing due to prior purchasing errors')
            return False

        return self.buyer.check_purchase_required(self.__in_nightmode)

    def failuretimeout(self) -> None:
        timeout_len = self.user_settings['captcha_failure_timeout']

        timeout_len = timeout_len*60 + random.uniform(0, 5*60)
        self.__log(f'Sleeping for {timeout_len} seconds')
        try:
            time.sleep(timeout_len)
        except KeyboardInterrupt:
            self.__log("Failure timeout sleep interrupted by user. Exiting...")
            raise
        self.__failure_timeout = False

    def on_cooldown(self) -> bool:
        return self.__cooldown or self.roc.on_cooldown()

    def handlecooldown(self) -> bool:
        if not self.on_cooldown():
            self.consecutive_cooldowns = 0
            return False

        self.roc.reset_cooldown()
        self.consecutive_cooldowns += 1
        return True

    def __recruitCheck(self) -> bool:
        captchaType = self.roc.recruit_has_captcha()
        if captchaType == Captcha.CaptchaType.TEXT:
            self.__log('Detected text captcha in recruit')
            self.__cooldown = True
            return False

        if captchaType is not None:
            self.__log('Attempting recruit captcha...')
            captcha = self.__handle_captcha(captchaType)

            if captcha is None or not captcha.ans_correct:
                self.__log('Bad captcha answer...')
                self.__captcha_final(captcha)
                return False
            if captcha.type == Captcha.CaptchaType.EQUATION:
                self.__log('Successfully solved equation')
                return False
            if self.roc.recruit_has_captcha():
                self.__log('Recruit attempt failed')
                return False
            self.__captcha_final(captcha)  # Log/Report
        else:
            self.__log("No captcha needed")
        return True

    def _is_purchase_successful(self) -> bool:
        return not self.__check_buy_needed()

    def __armoryCheck(self) -> bool:
        buy_needed = self.__check_buy_needed()

        if not buy_needed:
            self.__log("Armory purchase not needed")
            return True

        self.__log("Attempting to purchase...")
        payload = self.buyer.create_order_payload()

        itemcount = 0

        for ic in payload.values():
            if len(ic) > 0:
                itemcount += int(ic)

        if itemcount == 0:
            self.__log('Purchase payload is only 0 items.')
            return True

        self.__log(f'Purchasing {itemcount} items')

        res_captcha = self.__handle_img_captcha('roc_armory', payload)

        curtime = datetime.datetime.now()
        if self.__last_purchase_time:
            min_bugged_time = datetime.timedelta(0, 600)
            if (not res_captcha or res_captcha.ans in self.validans) \
                    and curtime - self.__last_purchase_time <= min_bugged_time:
                self.consecutive_purchase_attempts += 1
                time.sleep(3 + int(random.uniform(0, 1) * 5))
            elif res_captcha:
                self.consecutive_purchase_attempts = 0

        self.__last_purchase_time = curtime

        if res_captcha is None:
            return False

        if res_captcha.type and res_captcha.type == Captcha.CaptchaType.TEXT:
            self.__cooldown = True
            self.__log('Detected text captcha in armory')
            return False

        if not res_captcha.ans_correct:
            self.__captcha_final(res_captcha)
            self.__log('Bad captcha answer')
            return False
        purchase_success = self._is_purchase_successful()

        if not purchase_success:
            self.__log('Failure purchasing')
            self.__log(f'Payload was: {payload}')
        else:
            self.__log('Purchase was successful')

        self.__captcha_final(res_captcha)

        return res_captcha.ans_correct and purchase_success

    def __trainingCheck(self) -> bool:
        page = self.roc.get_training_page()

        if self.__training_error:
            self.__log('Not training due to passed failed attempts')
            return True

        if (self._trainer is None
                or not self._trainer.is_training_required(page)):
            self.__log('Training not needed')
            return True
        self.__log('Attempting to train our soldiers.')
        payload = self._trainer.gen_purchase_payload(tpage=page)

        res_captcha = self.__handle_img_captcha('roc_training', payload)

        curtime = datetime.datetime.now()
        if self.__last_train_time:
            min_bugged_time = datetime.timedelta(0, 600)
            if (not res_captcha or res_captcha.ans in self.validans) \
                    and curtime - self.__last_train_time <= min_bugged_time:
                self.consecutive_training_attempts += 1
                time.sleep(3 + int(random.uniform(0, 1) * 5))
            elif res_captcha:
                self.consecutive_training_attempts = 0

        self.__last_train_time = curtime

        if res_captcha is None:
            return False

        if res_captcha.type and res_captcha.type == Captcha.CaptchaType.TEXT:
            self.__cooldown = True
            self.__log('Detected text captcha in armory')
            return False

        if not res_captcha.ans_correct:
            self.__captcha_final(res_captcha)
            self.__log('Bad captcha answer')
            return False

        page = self.roc.get_training_page()
        train_success = not self._trainer.is_training_required(page)

        if not train_success:
            self.__log('Failure training')
        else:
            self.__log('Training was successful')

        self.__captcha_final(res_captcha)

        return res_captcha.ans_correct and train_success

    def _get_events(self) -> None:
        a = random.randint(1, 2)
        if not self.__in_nightmode and a != 1:
            return

        url = self.roc.url_generator.get_home() + '/base.php'
        self.roc.go_to_page(url)
        soup = bs4.BeautifulSoup(self.roc.r.text, 'lxml')
        base = pages.RocBasePage(soup)

        self.__log('-------------Event Status--------------')
        if len(base.current_events) > 0:
            self.__log('!! Current Events !!')
        else:
            self.__log('No events currently running')

        for event in base.current_events:
            self.__log(
                f'{event.name} | '
                + f'Ends at {event.date.strftime("%H:%M:%S")} |'
                + f' {event.description}')

        self.__log('')
        if len(base.upcoming_events) > 0:
            self.__log('-- Upcoming Events --')
        else:
            self.__log('No upcoming events')

        for event in base.upcoming_events:
            self.__log(
                f'{event.name} | '
                + f'Starts at {event.date.strftime("%H:%M:%S")} |'
                + f' {event.description}')
        self.__log('---------------------------------------')

    def start(self) -> None:
        self.__init_cookie_loading()
        self.consecutive_login_failures = 0
        self.consecutive_captcha_failures = 0
        self.consecutive_answer_errors = 0
        self.consecutive_bugged_logins = 0
        self.consecutive_purchase_attempts = 0
        self.consecutive_training_attempts = 0
        self.consecutive_cooldowns = 0
        while True:
            failure_conditions = self.__check_failure_conditions()
            if failure_conditions:
                failure_message = '\n'.join(failure_conditions)
                self.__log('Failure conditions met. Breaking loop.')
                raise Exception(f'Failure conditions met:\n{failure_message}')
            if self.__failure_timeout:
                if self.user_settings['captcha_failure_timeout'] <= 0:
                    self.__log('Failure timeout disabled. Exiting..')
                    raise Exception('Failure timeout disabled. Exiting..')
                self.failuretimeout()

            if self.handlecooldown():
                try:
                    time.sleep(self.consecutive_cooldowns * 15)
                except KeyboardInterrupt:
                    self.__log("Cooldown sleep interrupted by user. Exiting...")
                    raise
                continue

            # if not logged in and login attempt fails, retry after a bit
            if not self.roc.is_logged_in():
                self.__attempt_login()
                continue

            if not self.__trainingCheck():
                continue

            if not self.__armoryCheck():
                continue

            if not self.__recruitCheck():
                continue

            self._get_events()

            self.__sleep()
        self.__log("Main loop exited.")

    def __load_browser_cookies(self) -> bool:
        if self.user_settings['load_cookies_from_browser']:
            cookies = load_cookies_from_browser(
                self.user_settings['browser'],
                self.roc.url_generator.get_home()
                )
            self.roc.add_cookies(cookies)
            return True
        return False

    def __load_cookies_file(self) -> bool:
        if exists(self.cookie_filename):
            self.__log("Loading saved cookies")
            cookies = load_cookies_from_path(self.cookie_filename)
            if cookies is not None:
                self.roc.add_cookies(cookies)
