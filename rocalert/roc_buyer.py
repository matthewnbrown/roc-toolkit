
from rocalert.roc_web_handler import RocWebHandler, Captcha
from rocalert.captcha.captcha_logger import CaptchaLogger

BASE_PAYLOAD = {
    'sell[7]':'',
    'sell[8]':'',
    'sell[11]':'',
    'sell[13]':'',
    'sell[14]':'',
    }
for i in range(1,15):
    k = 'buy[{}]'.format(str(i))
    BASE_PAYLOAD[k] = ''

class ROCBuyer():
    def __init__(self, roc_handler: RocWebHandler, correctLogger: CaptchaLogger = None, genLogger: CaptchaLogger = None) -> None:
        if roc_handler is None:
            raise Exception("Parameter roc_handler must not be None")

        self.roc = roc_handler
        self._genlog = genLogger
        self.correctlog = correctLogger

    def create_order_payload() -> dict:
        
        return {}

    
