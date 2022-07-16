from abc import abstractclassmethod
from rocalert.roc_settings.settingstools import Settings
from rocalert.roc_web_handler import Captcha


class ROCService():
    """Generic class for a ROC service"""
    @abstractclassmethod
    def __init__(self, settings: Settings = None, name: str = None) -> None:
        if name is None:
            self.name = 'ROC Service'

        self.settings = settings

    """"Check if service succeeded (i.e., login success) """
    @abstractclassmethod
    def service_succeeded(self) -> bool:
        raise NotImplementedError

    """Runs the service"""
    @abstractclassmethod
    def run_service(self) -> bool:
        raise NotImplementedError

    """Does running this service require a captcha"""
    @abstractclassmethod
    def requires_captcha(self) -> bool:
        raise NotImplementedError

    """Returns the captcha from the service page"""
    @abstractclassmethod
    def get_captcha(self) -> Captcha:
        raise NotImplementedError

    """Solves a captcha, storing answer within the captcha"""
    @staticmethod
    def __solve_captcha(captcha: Captcha) -> Captcha:
        pass
