from http.client import RemoteDisconnected
from rocalert.roc_settings.settingstools import SiteSettings
from rocalert.captcha.pyroccaptchaselector import *

import requests # py -m pip install requests

class Captcha:
    def __init__(self, hash: str, img, ans: str = '-1', correct: bool = False) -> None:
        self._hash = hash
        self._img = img
        self._ans = ans
        self._ans_correct = correct
    @property
    def hash(self): return self._hash
    @property
    def img(self): return self._img
    @property
    def ans(self): return self._ans
    @ans.setter
    def ans(self, value: str): self._ans = value
    @property
    def ans_correct(self): return self._ans_correct
    @ans_correct.setter
    def ans_correct(self, correct: bool): self._ans_correct = correct

class RocWebHandler:
    def __init__(self, roc_site_settings) -> None:
        self.headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.63 Safari/537.36'}
        self.site_settings = roc_site_settings.get_settings()
        self.session = requests.Session()
        self.r = None

    def __go_to_page(self,url) -> requests.Response:
        try:
            self.r = self.session.get(url, headers=self.headers)
        except RemoteDisconnected as e:
            print("Error: Session disconnected! Attempting to reconnect...")
            cookies = self.session.cookies
            self.session = requests.Session()
            self.session.cookies.update(cookies)
            self.r = self.session.get(url, headers=self.headers)
            print('Success!')
        return self.r

    def __page_captcha_type(self) -> str:
        if '[click the correct number to proceed]' in self.r.text:
            return 'img'
        if '<h1>What is' in self.r.text:
            return 'equation'
        return None

    def __get_imagehash(self) -> str:
        index = self.r.text.find('img.php?hash=')
        if index == -1:
            return None
        imghash = self.r.text[index + len('img.php?hash='): self.r.text.find('"', index, index+100)]
        return imghash

    def get_img_captcha(self) -> Captcha:
        hash = self.__get_imagehash()

        if hash is None:
            return None

        img = self.__get_captcha_image(hash)
        return Captcha(hash, img)

    def get_equation_captcha(self) -> Captcha:
        index = self.r.text.find('<h1>What is')
        if index == -1:
            return None
        equation = self.r.text[index + len('<h1>What is'): self.r.text.find('</h1>', index, index+100)]
        equation = equation.strip()[:-1]
        c = Captcha(equation,None)
        return c

    def __get_captcha_image(self, hash):
        imgurl = 'img.php?hash=' + hash
        img = self.__go_to_page(self.site_settings['roc_home'] + imgurl).content
        return img

    def is_logged_in(self) -> bool:
        self.__go_to_page(self.site_settings['roc_home'])
        return r'email@address.com' not in self.r.text

    def login(self, email: str, password: str) -> bool:
        payload = {
            'email': email,
            'password': password
        }
        self.r = self.session.post(self.site_settings['roc_login'], payload)
        return r'Incorrect login' not in self.r.text
        
    def add_cookies(self, cookies) -> None:
        self.session.cookies.update(cookies)

    def get_cookies(self):
        return self.session.cookies
    def create_order_payload(order: dict) -> str:
        return ''
    def submit_equation(self, captcha: Captcha) -> bool:
        payload = {
            'flagInput':str(captcha.ans),
            'flagSubmit':'Submit'
        }
        self.r = self.session.post(self.site_settings['roc_recruit'], payload)

        return self.__page_captcha_type() == 'img'

    def submit_captcha(self, captcha: Captcha, ans: str) -> bool:
        cs = ROCCaptchaSelector()
        ans_coords = cs.get_xy_static(ans)

        payload = {
            'captcha': captcha.hash,
            'coordinates[x]':ans_coords[0],
            'coordinates[y]':ans_coords[1],
            'num':ans,
        }
        self.r = self.session.post(self.site_settings['roc_recruit'], payload)
        return not 'Wrong number' in self.r.text or 'wrong number' in self.r.text

    def recruit_has_captcha(self) -> str:
        self.__go_to_page(self.site_settings['roc_recruit'])
        return self.__page_captcha_type()