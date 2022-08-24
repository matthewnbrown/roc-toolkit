from abc import abstractmethod
from rocalert.roc_settings.settingstools import UserSettings
from rocalert.roc_web_handler import RocWebHandler


class RocService():
    """Generic class for a ROC service"""

    """Runs the service"""
    @classmethod
    @abstractmethod
    def run_service(
            roc: RocWebHandler = None,
            settings: UserSettings = None,
            custom_settings: dict = None
            ) -> bool:
        raise NotImplementedError

    """Solves a captcha, storing answer within the captcha"""
    @staticmethod
    def __check_params(
            roc: RocWebHandler = None,
            settings: UserSettings = None,
            custom_settings: dict = None
            ) -> dict:
        r, e = 'response', 'error'
        if roc is None:
            return {r: 'failure', e: 'roc session not passed in request'}
        if settings is None:
            return {r: 'failure', e: 'User settings not passed in request'}
        if custom_settings is None:
            return {r: 'failure', e: 'No custom settings passed in request'}
        return None
