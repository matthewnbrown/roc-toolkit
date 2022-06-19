import requests
#from roc_web_handler import Captcha

add_url = ''
lookup_url = ''

class Captcha():
    def __init__(self, hash, ans) -> None:
        self.hash = hash
        self.ans = ans

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

if __name__ == "__main__":
    l = r'https://rochash.azurewebsites.net/api/HashLookup?code=b8xX1DiL_gQ_07ZJ-mpKnPBwwwPY6bXKK40Li-8DVIobAzFu51phLg=='
    add_url = r'https://rochash.azurewebsites.net/api/AddHashAns?code=Npz0xiHFHhzbdgC3umU9JgDyUmws6KJjiC_kthW1HFtJAzFu02uMhg=='
    r = RemoteCaptcha(add_url, l)
    c = Captcha('abc123', 'sfsdafsa')

    print(r.lookup_remote(c));

