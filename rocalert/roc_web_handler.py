from http.client import RemoteDisconnected

from urllib3 import Retry
from rocalert.captcha.pyroccaptchaselector import ROCCaptchaSelector

import requests  # py -m pip install requests


def __generate_useragent():
    pass


class Captcha:
    def __init__(
            self, hash: str, img, ans: str = '-1',
            correct: bool = False
            ) -> None:

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
        self.headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; '
                        + 'Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                        + 'Chrome/102.0.5005.63 Safari/537.36'}
        self.site_settings = roc_site_settings.get_settings()
        self.session = requests.Session()

        retry = Retry(connect=10, backoff_factor=0.5)
        adapter = requests.adapters.HTTPAdapter(max_retries=retry)
        self.session.mount('http://', adapter)
        self.session.mount('https://', adapter)

        self.r = None

    def __check_for_bad_captcha(self):
        if 'cooldown' in self.r.url:
            for i in range(10):
                print('ERROR: RECEIVED TEXT CAPTCHA')
            print('Exiting...')
            quit()

    def __go_to_page(self, url) -> requests.Response:
        try:
            self.r = self.session.get(
                url,
                headers=self.headers,
                allow_redirects=True)
        except RemoteDisconnected:
            print("Error: Session disconnected! Attempting to reconnect...")
            cookies = self.session.cookies
            self.session = requests.Session()
            self.session.cookies.update(cookies)
            self.r = self.session.get(url, headers=self.headers)
            print('Success!')
        self.__check_for_bad_captcha()
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
        endIndex = self.r.text.find('"', index, index+100)
        imghash = self.r.text[index + len('img.php?hash='): endIndex]
        return imghash

    def get_img_captcha(self, page: str) -> Captcha:
        if page is None:
            return None

        self.__go_to_page(self.site_settings[page])
        hash = self.__get_imagehash()

        if hash is None:
            return None

        img = self.__get_captcha_image(hash)
        return Captcha(hash, img)

    def get_equation_captcha(self) -> Captcha:
        index = self.r.text.find('<h1>What is')
        if index == -1:
            return None
        endIndex = self.r.text.find('</h1>', index, index+100)
        equation = self.r.text[index + len('<h1>What is'):  endIndex]
        equation = equation.strip()[:-1]
        return Captcha(equation, None)

    def __get_captcha_image(self, hash):
        imgurl = self.site_settings['roc_home'] + 'img.php?hash=' + hash
        img = self.__go_to_page(imgurl).content
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
        incorrect = r'Incorrect login' in self.r.text
        return not incorrect and r'email@address.com' not in self.r.text
    
    def detailed_login(self, email: str, password: str) -> bool:
        payload = {
            'email': email,
            'password': password
        }
        self.r = self.session.post(self.site_settings['roc_login'], payload)
        if r'Incorrect login' in self.r.text:
            return 'incorrect_login'
        if r'email@address.com' in self.r.text:
            return 'general_failure'
        return 'success'

    def add_cookies(self, cookies) -> None:
        self.session.cookies.update(cookies)

    def get_cookies(self):
        return self.session.cookies

    def create_order_payload(order: dict) -> str:
        return ''

    def submit_equation(
            self, captcha: Captcha,
            page: str = 'roc_recruit'
            ) -> bool:
        payload = {
            'flagInput': str(captcha.ans),
            'flagSubmit': 'Submit'
        }
        self.r = self.session.post(self.site_settings[page], payload)

        return self.__page_captcha_type() == 'img'

    def submit_captcha(
            self, captcha: Captcha,
            ans: str,
            page: str,
            payload: dict = None
            ) -> bool:

        cs = ROCCaptchaSelector()
        x, y = cs.get_xy_static(ans, page)
        if payload is None:
            payload = {}

        payload['captcha'] = captcha.hash,
        payload['coordinates[x]'] = x,
        payload['coordinates[y]'] = y,
        payload['num'] = ans,

        self.r = self.session.post(self.site_settings[page], payload)
        return 'Wrong number' not in self.r.text or \
            'wrong number' in self.r.text

    def recruit_has_captcha(self) -> str:
        self.__go_to_page(self.site_settings['roc_recruit'])
        return self.__page_captcha_type()

    def current_gold(self) -> int:
        searchitem = r'<span id="s_gold">'
        index = self.r.text.index(searchitem)
        endIndex = self.r.text.find(r'</span>', index, index+100)
        goldstr = self.r.text[index + len(searchitem): endIndex]
        return int(goldstr.strip().replace(',', ''))

    def send_armory_order(self, payload: dict):
        pass
