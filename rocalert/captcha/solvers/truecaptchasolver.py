import base64

import requests

from rocalert.roc_web_handler import Captcha


class TrueCaptchaSolver:
    def __init__(self, userid: str, api_key: str, api_url: str = None, mode="default"):
        self._userid = userid
        self._api_key = api_key
        self._api_url = api_url or "https://api.apitruecaptcha.org/one/gettext"
        self._mode = mode

    def solve(self, captcha: Captcha) -> str:
        imageb64 = base64.b64encode(captcha.img).decode("ascii")

        data = {
            "userid": self._userid,
            "apikey": self._api_key,
            "data": imageb64,
            "tag": captcha.hash,
            "numeric": True,
            "len_str": 1,
            "mode": "human",
        }

        response = requests.post(url=self._api_url, json=data, timeout=40)

        if response.status_code != 200:
            raise Exception("TrueCaptcha API returned non-200 status code")

        return response.json()

    def report_answer(self, captcha: Captcha):
        pass
