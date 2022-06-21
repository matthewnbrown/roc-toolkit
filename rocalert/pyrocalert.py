from rocalert.captcha.equation_solver import EquationSolver
from rocalert.cookiehelper import *
from rocalert.captcha.roc_auto_solve import ROCCaptchaSolver
from rocalert.remote_lookup import RemoteCaptcha
from rocalert.roc_settings.settingstools import UserSettings, SiteSettings
from rocalert.roc_web_handler import RocWebHandler
from rocalert.roc_web_handler import Captcha
from rocalert.captcha.captcha_logger import CaptchaLogger

import io
import PIL.Image
import time
import datetime
import random
from os.path import exists


class RocAlert:
    def __init__(self, usersettings: UserSettings = None, sitesettings: SiteSettings = None, correctLog: CaptchaLogger = None, generalLog: CaptchaLogger = None, remoteCaptcha: RemoteCaptcha = None) -> None:
        self.user_settings = usersettings.get_settings()
        self.site_settings = sitesettings.get_settings()
        self.validans = { str(i) for i in range(1,10) }
        self.roc = RocWebHandler(sitesettings) 
        self.solver = ROCCaptchaSolver()     
        self.general_log = generalLog
        self.correct_log = correctLog
        if self.user_settings['auto_solve_captchas']:
            self.solver.set_twocaptcha_apikey(self.user_settings['auto_captcha_key'])

        self.cookie_filename = 'cookies'
        self.__useRemoteCatcha = True
        self.__remoteCaptcha = remoteCaptcha

    def __log(self, message : str, end = None, timestamp = True) -> None:
        if timestamp:
            ts = datetime.datetime.now().strftime("%H:%M:%S")
            print('{}: {}'.format(ts, message), end=end)
        else:
            print(message, end=end)

    def __get_waittime(self) -> int:
        if not self.__in_nightmode():
            min = self.user_settings['min_checktime_secs']
            max = self.user_settings['max_checktime_secs']
        else:
            min = self.user_settings['nightmode_minwait_mins'] * 60
            max = self.user_settings['nightmode_maxwait_mins'] * 60
        return min + int(random.uniform(0,1) * max)

    def __get_img_captcha_ans(self, captcha: Captcha) -> str:
        path = self.__save_captcha(captcha)

        if self.__useRemoteCatcha:
            res = self.__remoteCaptcha.lookup_remote(captcha)
            if res is not None and len(res) > 0:
                self.__log(f'Received result from remote: {res}')
                res = res.split(':',1)
                if len(res) == 2:
                    captcha.ans = res[1]
                    return captcha.ans

        if self.user_settings['auto_solve_captchas']:
            ans = self.solver.twocaptcha_solve(path)
        else:
            ans = self.solver.gui_solve(captcha.img)

        captcha.ans = ans
        return ans
    
    def __save_captcha(self, captcha: Captcha):
        img = PIL.Image.open(io.BytesIO(captcha.img))
        path = self.user_settings['captcha_save_path'] + captcha.hash + '.png'
        img.save(path)
        return path;
    
    def __log_general(self, captcha: Captcha):
        if self.general_log is not None:
            self.general_log.log_captcha(captcha)

    def __log_correct(self, captcha: Captcha):
        if self.correct_log is not None:
            self.correct_log.log_captcha(captcha=captcha)

    def __in_nightmode(self) -> bool:
        if not self.user_settings['enable_nightmode']:
            return False
        start, end = self.user_settings['nightmode_begin'], self.user_settings['nightmode_end']
        now = datetime.datetime.now().time()

        if start <= end :
            return start <= now <= end
        else:
            return start <= now or now <= end

    def __get_waittime(self) -> int:
        if not self.__in_nightmode():
            min = self.user_settings['min_checktime_secs']
            max = self.user_settings['max_checktime_secs']
        else:
            min = self.user_settings['nightmode_minwait_mins'] * 60
            max = self.user_settings['nightmode_maxwait_mins'] * 60
        return min + int(random.uniform(0,1) * max)  

    def __sleep(self) -> None:
        waitTime = self.__get_waittime()
        save_cookies_to_path(self.roc.get_cookies(), self.cookie_filename)
        endtime = datetime.datetime.now() + datetime.timedelta(0, waitTime)
        self.__log('Taking a nap. Waking up at {}.'.format(endtime.strftime('%H:%M:%S')))
        time.sleep(waitTime)

    def __attempt_login(self) -> bool:
        self.__log('Session timed out. ', end = '')
        if self.__load_browser_cookies() and self.roc.is_logged_in():
            self.__log('Successfully pulled cookie from {}'.format(self.user_settings['browser']), timestamp=False)
            return True

        res = self.roc.login(self.user_settings['email'], self.user_settings['password'])

        if res:
            self.consecutive_login_failures = 0
            self.__log("Login success.", timestamp=False)
            save_cookies_to_path(self.roc.get_cookies(), self.cookie_filename)
        else:
            self.consecutive_login_failures += 1
            self.__("Login failure.", timestamp=False)
            return False

    def __report_captcha(self, captcha: Captcha):
        if self.user_settings['auto_solve_captchas'] and captcha.img is not None:
            self.solver.report_last_twocaptcha(captcha.ans_correct)

    def __captcha_final(self, captcha: Captcha) -> None:
        if captcha.img is None:
            return

        if 'ERROR' not in captcha.ans:
            self.__report_captcha(captcha)
        
        if captcha.ans_correct:
            self.__log_correct(captcha)
        if captcha.ans_correct and self.__useRemoteCatcha:
            self.__remoteCaptcha.add_remote(captcha)

        self.__log_general(captcha)

    def __handle_img_captcha(self) -> Captcha:
        captcha = self.roc.get_img_captcha()
        ans = self.__get_img_captcha_ans(captcha)
        captcha.ans_correct = False
        if len(ans) != 1 or ans not in self.validans:
            self.__log("Warning: received response \'{}\' from captcha solver!".format(ans))
            if 'bad response: 503' in ans:
                self.__log("Waiting 5 seconds before attempting again...")
                time.sleep(5)
            self.consecutive_answer_errors += 1
            return captcha
        else:
            self.__log('Received answer: \'{}\': '.format(ans), end='')

        self.consecutive_answer_errors = 0  
        correct = self.roc.submit_captcha(captcha, ans)
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
        time.sleep(minsleeptime + int(random.uniform(0,1) * minsleeptime))

        correct = self.roc.submit_equation(c)

        if correct:
            self.__log(f"{c.hash} = {c.ans}")
            self.consecutive_captcha_failures = 0
        else:
            self.__log(f"{c.hash} != {c.ans}... oops")
            self.consecutive_captcha_failures += 1
        return c
        
    def __handle_captcha(self, captchaType: str) -> Captcha:
        self.__log(f'Detected {captchaType} captcha...')

        if captchaType == 'img':
            return self.__handle_img_captcha();
        elif captchaType == 'equation':
            return self.__handle_equation_captcha()
        
        return None

    def __init_cookie_loading(self) -> None:
        self.__load_browser_cookies()
        if not self.roc.is_logged_in():
            self.__load_cookies_file()
        else:
            self.__log("Took login cookie from browser.")

    def __check_failure_conditions(self) -> bool:
        error = False
        if self.consecutive_login_failures >= self.user_settings['max_consecutive_login_failures']:
            self.__log("ERROR: Multiple login failures. Exiting.")
            error = True
        if self.consecutive_answer_errors >= self.user_settings['max_consecutive_answer_errors']:
            self.__log("Too many consecutive bad answers received, exiting!")
            error = True
        if self.consecutive_captcha_failures >= self.user_settings['max_consecutive_captcha_attempts']:
            self.__log("Failed too many captchas, exiting!")
            error = True
        return error

    def start(self) -> None:
        self.__init_cookie_loading()
        self.consecutive_login_failures = 0
        self.consecutive_captcha_failures = 0
        self.consecutive_answer_errors = 0
        while True: 
            if self.__check_failure_conditions():
                break

            # if not logged in and login attempt fails, retry after a bit
            if not self.roc.is_logged_in():
                self.__attempt_login()
                continue

            captchaType = self.roc.recruit_has_captcha()
            if captchaType is not None:
                captcha = self.__handle_captcha(captchaType)
                self.__captcha_final(captcha) # Log/Report
                if not captcha.ans_correct:
                    continue 
            else:
                self.__log("No captcha needed")
        
            self.__sleep()
        self.__log("Main loop exited.")

    def __load_browser_cookies(self) -> bool:
        if self.user_settings['load_cookies_from_browser']:
            cookies = load_cookies_from_browser(self.user_settings['browser'], self.site_settings['roc_home'])
            self.roc.add_cookies(cookies)
            return True
        return False

    def __load_cookies_file(self) -> bool:
        if exists(self.cookie_filename):
            self.__log("Loading saved cookies")
            cookies = load_cookies_from_path(self.cookie_filename)
            if cookies is not None:
                self.roc.add_cookies(cookies)

