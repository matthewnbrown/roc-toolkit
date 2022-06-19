import requests
from rocalert.roc_web_handler import Captcha

class RemoteCaptcha():
    def __init__(self, add_url, lookup_url) -> None:
        self.__add_url = add_url
        self.__lookup_url = lookup_url

    def __get_result(self, url, payload):
        try:
            resp = requests.get(url, payload).text
        except Exception as e:
            resp = 'ERROR ACCESSING REMOTE'
        return resp

    def lookup_remote(self, captcha: Captcha) -> str:
        if self.__lookup_url is None:
            return None
        
        payload = { 'hash': captcha.hash }
        return self.__get_result(self.__lookup_url, payload)

    def add_remote(self, captcha: Captcha) -> str:
        if self.__add_url is None:
            return None

        payload = { 'hash':captcha.hash, 'answer':captcha.ans }
        return self.__get_result(self.__add_url, payload)



