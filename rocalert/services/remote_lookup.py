import requests
from rocalert.roc_web_handler import Captcha


class RemoteCaptcha():
    def __init__(self, add_url, lookup_url) -> None:
        self.__add_url = add_url
        self.__lookup_url = lookup_url

    def __get_result(self, url, payload):
        try:
            resp = requests.get(url, json=payload).json()
            result = resp['Answer']
        except Exception:
            result = 'ERROR ACCESSING REMOTE'
        return result

    def __put_result(self, captcha: Captcha):
        if self.__add_url is None or captcha is None:
            return

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
        if self.__lookup_url is None:
            return None

        payload = {'hash': captcha.hash}
        return self.__get_result(self.__lookup_url, payload)

    def add_remote(self, captcha: Captcha) -> str:
        if captcha.ans is None or captcha.hash is None:
            return
        if not captcha.ans_correct:
            return

        return self.__put_result(captcha)
