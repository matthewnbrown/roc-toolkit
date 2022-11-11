import requests
from rocalert.roc_web_handler import Captcha


class RemoteCaptcha():
    def __init__(self, add_url, lookup_url) -> None:
        self.__add_url = add_url
        self.__lookup_url = lookup_url

    def __get_result(self, captcha: Captcha):
        payload = {
            'hash': captcha.hash
            }
        try:
            resp = requests.get(self.__lookup_url, json=payload).json()
            result = resp['Answer']
        except Exception:
            result = 'ERROR ACCESSING REMOTE'
        return result

    def __put_result(self, captcha: Captcha):
        payload = {
            'hash': captcha.hash,
            'answer': captcha.ans}

        try:
            resp = requests.put(self.__add_url, json=payload)
            if resp.status_code != 200:
                result = resp.reason
            else:
                result = 'OK'
        except Exception:
            result = 'ERROR ACCESSING REMOTE'

        return result

    def lookup_remote(self, captcha: Captcha) -> str:
        if self.__lookup_url is None or 'None' in self.__lookup_url\
                or captcha is None or captcha.hash is None:
            return None

        return self.__get_result(captcha)

    def add_remote(self, captcha: Captcha) -> str:
        if captcha.ans is None or captcha.hash is None\
                or self.__add_url is None or 'None' == self.__add_url:
            return
        if not captcha.ans_correct:
            return

        return self.__put_result(captcha)
