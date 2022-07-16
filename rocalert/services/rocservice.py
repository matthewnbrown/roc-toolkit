from abc import abstractclassmethod
from rocalert.roc_settings.settingstools import UserSettings
from rocalert.roc_web_handler import RocWebHandler
from rocalert.roc_web_handler import Captcha


class RocService():
    """Generic class for a ROC service"""

    """Runs the service"""
    @abstractclassmethod
    def run_service(
            self,
            roc: RocWebHandler = None,
            settings: UserSettings = None,
            custom_settings: dict = None
            ) -> bool:
        raise NotImplementedError

    """Solves a captcha, storing answer within the captcha"""
    @classmethod
    def __solve_captcha(self, captcha: Captcha) -> Captcha:
        pass
