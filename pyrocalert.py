from cookiehelper import *
from pyroccaptchaselector import *
from pyrocaltertgui import get_user_answer_captcha
import roc_auto_solve
from settingstools import UserSettings, SiteSettings

import io
import PIL.Image
import time
import datetime
import random
import requests # py -m pip install requests
from os.path import exists

class RocAlert:
    def __init__(self, usersettings: UserSettings = None, sitesettings: SiteSettings = None) -> None:
        self.headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.63 Safari/537.36'}
        self.user_settings = usersettings.get_settings()
        self.site_settings = sitesettings.get_settings()
        self.validans = { str(i) for i in range(1,10) }
        self.session = requests.Session()
        self.cookie_filename = 'cookies'


    def __log(self, message : str, end = None) -> None:
        print(message, end=end)

    def go_to_page(self,url) -> requests.Response:
        return self.session.get(url, headers=self.headers)

    def is_logged_in(self, resp = None) -> bool:
        if resp is None:
            resp = self.go_to_page(self.site_settings['roc_home'])
        return r'email@address.com' not in resp.text
    
    def login(self) -> bool:
        payload = {
            'email':self.user_settings['email'],
            'password':self.user_settings['password']
        }
        p = self.session.post(self.site_settings['roc_login'], payload)
        return r'Incorrect login' not in p.text

    def get_waittime(self) -> int:
        if not self.in_nightmode():
            min = self.user_settings['min_checktime_secs']
            max = self.user_settings['max_checktime_secs']
        else:
            min = self.user_settings['nightmode_minwait_mins'] * 60
            max = self.user_settings['nightmode_maxwait_mins'] * 60
        return min + int(random.uniform(0,1) * max)
    
    def resp_has_captcha(r) -> bool:
        return '[click the correct number to proceed]' in r.text

    def get_imagehash_from_resp(resp) -> str:
        index = resp.text.find('img.php?hash=')
        imghash = resp.text[index + len('img.php?hash='):resp.text.find('"', index, index+100)]
        return imghash

    def get_captcha_image(self, hash):
        imgurl = 'img.php?hash=' + hash
        img = self.go_to_page(self.site_settings['roc_home'] + imgurl).content
        #with open('image_name.png', 'wb') as handler:
        #    handler.write(img)
        return img
    
    def send_captcha_ans(self, hash, ans) -> bool:
        cs = ROCCaptchaSelector()
        ans_coords = cs.get_xy_static(ans)
        print(ans, ans_coords)

        payload = {
            'captcha':hash,
            'coordinates[x]':ans_coords[0],
            'coordinates[y]':ans_coords[1],
            'num':ans,
        }
        p = self.session.post(self.site_settings['roc_recruit'], payload)
        return not RocAlert.resp_has_captcha(p)
    
    def get_captcha_ans(self, img, hash) -> str:
        path = self.save_captcha(img, hash)

        if self.user_settings['auto_solve_captchas']:
            return roc_auto_solve.Solve(self.user_settings['auto_captcha_key'], path)
        else:
            return get_user_answer_captcha(img)
    
    def save_captcha(self, img_bytes, hash):
        img = PIL.Image.open(io.BytesIO(img_bytes))
        path = self.user_settings['captcha_save_path'] + hash + '.png'
        img.save(path)
        return path;
    
    def in_nightmode(self) -> bool:
        if not self.user_settings['enable_nightmode']:
            return False
        start, end = self.user_settings['nightmode_begin'], self.user_settings['nightmode_end']
        now = datetime.datetime.now().time()

        if start <= end :
            return start <= now <= end
        else:
            return start <= now or now <= end

    def __get_waittime(self) -> int:
        if not self.in_nightmode():
            min = self.user_settings['min_checktime_secs']
            max = self.user_settings['max_checktime_secs']
        else:
            min = self.user_settings['nightmode_minwait_mins'] * 60
            max = self.user_settings['nightmode_maxwait_mins'] * 60
        return min + int(random.uniform(0,1) * max)  

    def __sleep(self) -> None:
        waitTime = self.__get_waittime()
        save_cookies_to_path(self.session.cookies, self.cookie_filename)
        endtime = datetime.datetime.now() + datetime.timedelta(0, waitTime)
        self.__log('Taking a nap. Waking up at {}.'.format(endtime.strftime('%H:%M:%S')))
        time.sleep(waitTime)

    def __attempt_login(self) -> bool:
        self.__log("Session timed out. Logging back in: ", end = "")
        res = self.login()
        if res:
            self.consecutive_login_failures = 0
            self.__log("Login success")
            save_cookies_to_path(self.session.cookies, self.cookie_filename)
        else:
            self.consecutive_login_failures += 1
            self.__("Login failure")
            return False

    def __handle_captcha(self, resp) -> bool:
        self.__log('Detected captcha...')
        hash = RocAlert.get_imagehash_from_resp(resp)
        img = self.get_captcha_image(hash)
        ans = self.get_captcha_ans(img, hash)
        if len(ans) != 1 or ans not in self.validans:
            self.__log("Warning: received response \'{}\' from captcha solver!".format(ans))
            self.consecutive_answer_errors += 1
            return False
    
        self.consecutive_answer_errors = 0  
        correct = self.send_captcha_ans(hash, ans)
        if correct:
            print("Correct answer")
            self.consecutive_captcha_failures = 0
        else:
            print("Incorrect answer")
            self.consecutive_captcha_failures += 1
            return False
        return True

    def start(self) -> None:
        self.load_cookies()
        self.consecutive_login_failures = 0
        self.consecutive_captcha_failures = 0
        self.consecutive_answer_errors = 0
        while True:
            if self.consecutive_login_failures >= self.user_settings['max_consecutive_login_failures']:
                self.__log("ERROR: Multiple login failures. Exiting.")
                break
            if self.consecutive_answer_errors >= self.user_settings['max_consecutive_answer_errors']:
                self.__log("Too many consecutive bad answers received, exiting!")
                break
            if self.consecutive_captcha_failures >= self.user_settings['max_consecutive_captcha_attempts']:
                print("Failed too many captchas, exiting!")
                break
            r = self.go_to_page(self.site_settings['roc_recruit'])

            # if not logged in and login attempt fails, retry after a bit
            if not self.is_logged_in(r):
                self.__attempt_login()
                continue

            if RocAlert.resp_has_captcha(r):
                self.__handle_captcha(r)   
            else:
                print("No captcha needed")
        
            self.__sleep()
        self.__log("Main loop exited.")

    def load_cookies(self) -> bool:
        if self.user_settings['load_cookies_from_browser']:
            cookies = load_cookies_from_browser()
            self.session.cookies.update(cookies)
        elif exists(self.cookie_filename):
            self.__log("Loading saved cookies")
            cookies = load_cookies_from_path(self.cookie_filename)
            self.session.cookies.update(cookies)

