from ...roc_web_handler import Captcha
from twocaptcha import TwoCaptcha
import PIL.Image
import io
import collections


class TwoCaptchaSolver:
    def __init__(self, api_key: str, savepath: str) -> None:
        self._solver = TwoCaptcha(apiKey=api_key)
        self._savepath = savepath
        self._lastresp = None
        self._hinttext = 'A single digit between 1 and 9'
        self._responsehistory = collections.deque(maxlen=10)

    def captcha_solve(self, captcha: Captcha):
        img = PIL.Image.open(io.BytesIO(captcha.img))
        path = f'{self._savepath}/{captcha.hash}.png'
        img.save(path)

        response = self._solver.normal(path, hintText=self._hinttext)
        self._responsehistory.append((captcha.hash, response))
        captcha.ans = response['code']
        return captcha

    def report_answer(self, captcha: Captcha):
        for chash, resp in self._responsehistory:
            if chash == captcha.hash:
                self._solver.report(resp['captchaId'], captcha.ans_correct)
                break
