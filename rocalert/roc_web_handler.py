import datetime
from http.client import RemoteDisconnected

import requests
from bs4 import BeautifulSoup
from urllib3 import Retry

import rocalert.pages as pages
from rocalert.services.urlgenerator import ROCUrlGenerator

from .captcha.pyroccaptchaselector import ROCCaptchaSelector

_BS_PARSER = "lxml"


def __generate_useragent():
    pass


class Captcha:
    class CaptchaType:
        TEXT = "text"
        IMAGE = "img"
        EQUATION = "equation"

    EXPIRATION_AGE = datetime.timedelta(minutes=4, seconds=30)

    def __init__(
        self,
        hash: str,
        img: bytes = None,
        ans: str = "-1",
        correct: bool = False,
        captype: str = None,
        creation_date: datetime.datetime = None,
    ) -> None:
        self._hash = hash
        self._img = img
        self._ans = ans
        self._ans_correct = correct
        self._type = captype

        if creation_date is None:
            self._creationdate = datetime.datetime.now()
        else:
            self._creationdate = creation_date

    @property
    def hash(self):
        return self._hash

    @property
    def img(self):
        return self._img

    @property
    def ans(self):
        return self._ans

    @ans.setter
    def ans(self, value: str):
        self._ans = value

    @property
    def ans_correct(self):
        return self._ans_correct

    @ans_correct.setter
    def ans_correct(self, correct: bool):
        self._ans_correct = correct

    @property
    def type(self):
        return self._type

    @property
    def creation_date(self) -> datetime.datetime:
        return self._creationdate

    @property
    def age(self) -> datetime.timedelta:
        return datetime.datetime.now() - self._creationdate

    @property
    def is_expired(self) -> bool:
        return self.age >= Captcha.EXPIRATION_AGE


class RocWebHandler:
    class Pages:
        TRAINER = "roc_training"
        RECRUIT = "roc_recruit"
        ARMORY = "roc_armory"
        HOME = "roc_home"
        LOGIN = "roc_login"

    def __init__(
        self,
        urlgenerator: ROCUrlGenerator,
        default_headers: dict[str, str] = None,
    ) -> None:
        if default_headers:
            self.headers = default_headers
        else:
            self.headers = {
                "Accept": "text/html,application/xhtml+xml,application/xml"
                + ";q=0.9,image/avif,image/webp,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.5",
                "Connection": "keep-alive",
                "Sec-Fetch-Dest": "document",
                "Sec-Fetch-Mode": "navigate",
                "Sec-Fetch-Site": "same-origin",
                "Sec-Fetch-User": "?1",
                "TE": "trailers",
                "Upgrade-Insecure-Requests": "1",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                + "AppleWebKit/537.36 (KHTML, like Gecko) "
                + "Chrome/114.0.0.0 Safari/537.36",
            }

        self._urlgenerator = urlgenerator
        self.session = requests.Session()

        retry = Retry(connect=10, backoff_factor=0.5)
        adapter = requests.adapters.HTTPAdapter(max_retries=retry)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        self.r = None

    def __check_for_bad_captcha(self):
        return "cooldown" in self.r.url

    def go_to_page(self, url):
        return self.__go_to_page(url)

    def __go_to_page(self, url) -> requests.Response:
        try:
            self.r = self.session.get(url, headers=self.headers, allow_redirects=True)
        except RemoteDisconnected:
            print("Error: Session disconnected! Attempting to reconnect...")
            cookies = self.session.cookies
            self.session = requests.Session()
            self.session.cookies.update(cookies)
            self.r = self.session.get(url, headers=self.headers)
            print("Success!")

        return self.r

    def __page_captcha_type(self) -> str:
        if self.__check_for_bad_captcha():
            return Captcha.CaptchaType.TEXT
        if "[click the correct number to proceed]" in self.r.text:
            return Captcha.CaptchaType.IMAGE
        if "<h1>What is" in self.r.text:
            return Captcha.CaptchaType.EQUATION
        return None

    def __get_imagehash(self) -> str:
        index = self.r.text.find("img.php?hash=")
        if index == -1:
            return None
        endIndex = self.r.text.find('"', index, index + 100)
        imghash = self.r.text[index + len("img.php?hash=") : endIndex]
        return imghash

    def get_url_img_captcha(self, url: str) -> Captcha:
        if url is None:
            return None

        self.__go_to_page(url)
        cap_type = self.__page_captcha_type()
        hash = self.__get_imagehash()

        if hash is None:
            return None

        img = self.__get_captcha_image(hash)
        return Captcha(hash, img, captype=cap_type)

    def get_img_captcha(self, page: str) -> Captcha:
        if page is None:
            return None

        self.__go_to_page(self._urlgenerator.get_page_url(page))
        cap_type = self.__page_captcha_type()
        hash = self.__get_imagehash()

        if hash is None:
            return None

        img = self.__get_captcha_image(hash)

        return Captcha(hash, img, captype=cap_type)

    def get_equation_captcha(self) -> Captcha:
        index = self.r.text.find("<h1>What is")
        if index == -1:
            return None
        endIndex = self.r.text.find("</h1>", index, index + 100)
        equation = self.r.text[index + len("<h1>What is") : endIndex]
        equation = equation.strip()[:-1]
        return Captcha(equation, None, captype=Captcha.CaptchaType.EQUATION)

    def __get_captcha_image(self, hash):
        imgurl = self._urlgenerator.get_home() + "/img.php?hash=" + hash

        img = self.__go_to_page(imgurl).content
        return img

    def is_logged_in(self) -> bool:
        self.__go_to_page(self._urlgenerator.get_home())
        return r"email@address.com" not in self.r.text

    def login(self, email: str, password: str) -> bool:
        payload = {"email": email, "password": password}
        self.r = self.session.post(
            self._urlgenerator.get_login(), payload, headers=self.headers
        )
        incorrect = r"Incorrect login" in self.r.text
        return not incorrect and r"email@address.com" not in self.r.text

    def detailed_login(self, email: str, password: str) -> bool:
        payload = {"email": email, "password": password}
        self.r = self.session.post(
            self._urlgenerator.get_login(), payload, headers=self.headers
        )
        if r"Incorrect login" in self.r.text:
            return "incorrect_login"
        if r"email@address.com" in self.r.text:
            return "general_failure"
        return "success"

    def add_cookies(self, cookies) -> None:
        self.session.cookies.update(cookies)

    def get_cookies(self):
        return self.session.cookies

    def create_order_payload(order: dict) -> str:
        return ""

    def submit_equation(self, captcha: Captcha, page: str = "roc_recruit") -> bool:
        payload = {"flagInput": str(captcha.ans), "flagSubmit": "Submit"}
        self.r = self.session.post(
            self._urlgenerator.get_page_url(page),
            payload,
            headers=self.headers,
        )

        return self.__page_captcha_type() == Captcha.CaptchaType.IMAGE

    def _check_incorrect_captcha(self) -> bool:
        return "Wrong number" not in self.r.text or "wrong number" in self.r.text

    def submit_captcha_url(
        self, captcha: Captcha, url: str, payload: dict = None, manual_page: str = None
    ) -> bool:
        if payload is None:
            payload = {}

        payload["captcha"] = captcha.hash
        if manual_page:
            x, y = ROCCaptchaSelector().get_xy_static(captcha.ans, manual_page)
        else:
            x, y = 0, 0
        payload["coordinates[x]"] = x
        payload["coordinates[y]"] = y
        payload["manualcaptcha"] = captcha.ans if not manual_page else ""
        if manual_page:
            payload["num"] = captcha.ans

        self.r = self.session.post(url, payload, headers=self.headers)
        return self._check_incorrect_captcha()

    def submit_captcha(
        self, captcha: Captcha, ans: str, page: str, payload: dict = None
    ) -> bool:
        cs = ROCCaptchaSelector()
        x, y = cs.get_xy_static(ans, page)
        if payload is None:
            payload = {}

        payload["captcha"] = captcha.hash
        payload["coordinates[x]"] = x
        payload["coordinates[y]"] = y
        payload["manualcaptcha"] = ""
        payload["num"] = ans

        self.r = self.session.post(
            self._urlgenerator.get_page_url(page), payload, headers=self.headers
        )

        return self._check_incorrect_captcha()

    def get_imgcap_from_hash(self, hash: str) -> bytes:
        return self.__get_captcha_image(hash)

    def recruit_has_captcha(self) -> str:
        self.__go_to_page(self._urlgenerator.get_recruit())
        return self.__page_captcha_type()

    def current_gold(self) -> int:
        searchitem = r'<span id="s_gold">'
        index = self.r.text.index(searchitem)
        endIndex = self.r.text.find(r"</span>", index, index + 100)
        goldstr = self.r.text[index + len(searchitem) : endIndex]
        return int(goldstr.strip().replace(",", ""))

    def reset_cooldown(self) -> None:
        addition = r"/cooldown.php?delete=strike"
        self.__go_to_page(self._urlgenerator.get_home() + addition)

    def on_cooldown(self) -> bool:
        self.go_to_armory()
        return self.__page_captcha_type() == Captcha.CaptchaType.TEXT

    def go_to_armory(self) -> None:
        self.__go_to_page(self._urlgenerator.get_armory())

    def go_to_training(self) -> None:
        self.__go_to_page(self._urlgenerator.get_training())

    def go_to_keep(self) -> None:
        self.__go_to_page(self._urlgenerator.get_keep())

    def get_response(self) -> requests.Response:
        return self.r

    def get_page_captcha_type(self, url) -> str:
        self.__go_to_page(url)
        return self.__page_captcha_type()

    def send_armory_order(self, payload: dict):
        pass

    def get_training_page(self) -> pages.RocTrainingPage:
        self.go_to_training()
        soup = BeautifulSoup(self.r.text, _BS_PARSER)
        return pages.RocTrainingPage(soup)

    def get_armory_page(self) -> pages.RocArmoryPage:
        self.go_to_armory()
        soup = BeautifulSoup(self.r.text, _BS_PARSER)
        return pages.RocArmoryPage(soup)

    def get_keep_page(self) -> pages.RocKeepPage:
        self.go_to_keep()
        soup = BeautifulSoup(self.r.text, _BS_PARSER)
        return pages.RocKeepPage(soup)

    def get_attack_page(self, target_id) -> pages.RocAttackPage:
        self.__go_to_page(self._urlgenerator.get_attack(target_id))
        soup = BeautifulSoup(self.r.text, _BS_PARSER)
        return pages.RocAttackPage(soup)

    def start_key_repair(self) -> None:
        pass

    @property
    def url_generator(self) -> ROCUrlGenerator:
        return self._urlgenerator
