from ast import Raise
import imp
from roc_web_handler import RocWebHandler, Captcha
from rocalert.captcha.captcha_logger import CaptchaLogger



class ROCBuyer():
    def __init__(self, roc_handler: RocWebHandler, correctLogger: CaptchaLogger = None, genLogger: CaptchaLogger = None) -> None:
        if roc_handler is None:
            raise Exception("Parameter roc_handler must not be None")

        self.roc = roc_handler
        self._genlog = genLogger
        self.correctlog = correctLogger

    def create_order_payload() -> dict:
        return {}

    
