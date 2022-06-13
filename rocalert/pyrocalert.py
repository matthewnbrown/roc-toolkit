from rocalert.cookiehelper import *
from rocalert.captcha.roc_auto_solve import ROCCaptchaSolver
from rocalert.roc_settings.settingstools import UserSettings, SiteSettings
from rocalert.roc_web_handler import RocWebHandler

import io
import PIL.Image
import time
import datetime
import random
from os.path import exists

from rocalert.roc_web_handler import Captcha

class RocAlert:
    def __init__(self, usersettings: UserSettings = None, sitesettings: SiteSettings = None) -> None:
        self.user_settings = usersettings.get_settings()
        self.site_settings = sitesettings.get_settings()
        self.validans = { str(i) for i in range(1,10) }
        self.roc = RocWebHandler(sitesettings) 
        self.solver = ROCCaptchaSolver()     
        
        if self.user_settings['auto_solve_captchas']:
            self.solver.set_twocaptcha_apikey(self.user_settings['auto_captcha_key'])

        self.cookie_filename = 'cookies'

    def __log(self, message : str, end = None) -> None:
        print(message, end=end)

    def __get_waittime(self) -> int:
        if not self.__in_nightmode():
            min = self.user_settings['min_checktime_secs']
            max = self.user_settings['max_checktime_secs']
        else:
            min = self.user_settings['nightmode_minwait_mins'] * 60
            max = self.user_settings['nightmode_maxwait_mins'] * 60
        return min + int(random.uniform(0,1) * max)
    
    def __get_captcha_ans(self, captcha: Captcha) -> str:
        path = self.__save_captcha(captcha)

        if self.user_settings['auto_solve_captchas']:
            return self.solver.twocaptcha_solve(path)
        else:
            return self.solver.gui_solve(captcha.img)
    
    def __save_captcha(self, captcha: Captcha):
        img = PIL.Image.open(io.BytesIO(captcha.img))
        path = self.user_settings['captcha_save_path'] + captcha.hash + '.png'
        img.save(path)
        return path;
    
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
            self.__log('Successfully pulled cookie from {}'.format(self.user_settings['browser']))
            return True

        res = self.roc.login()
        if res:
            self.consecutive_login_failures = 0
            self.__log("Login success.")
            save_cookies_to_path(self.roc.get_cookies(), self.cookie_filename)
        else:
            self.consecutive_login_failures += 1
            self.__("Login failure.")
            return False

    def __handle_captcha(self) -> bool:
        self.__log('Detected captcha...')

        captcha = self.roc.get_captcha()
        ans = self.__get_captcha_ans(captcha)

        if len(ans) != 1 or ans not in self.validans:
            self.__log("Warning: received response \'{}\' from captcha solver!".format(ans))
            self.consecutive_answer_errors += 1
            return False
        else:
            self.__log('Received answer: \'{}\': '.format(ans), end='')

        self.consecutive_answer_errors = 0  
        correct = self.roc.submit_captcha(captcha, ans)
        if correct:
            self.__log("Correct answer")
            self.consecutive_captcha_failures = 0
        else:
            self.__log("Incorrect answer")
            self.consecutive_captcha_failures += 1
            return False
        return True

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

            if self.roc.recruit_has_captcha():
                correct = self.__handle_captcha()
                if not correct:
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
            self.roc.add_cookies(cookies)

