from rocalert.rocaccount import ROCTraining, RocItem, ROCAccount, ROCArmory, ROCStats
from rocalert.roc_settings.settingstools import UserSettings
from rocalert.roc_web_handler import RocWebHandler
from rocalert.roc_web_handler import Captcha
from rocalert.services.rocservice import RocService


class GetGold(RocService):
    @classmethod
    def run_service(
            roc: RocWebHandler = None,
            settings: UserSettings = None,
            custom_settings: dict = None
            ) -> bool:
        raise NotImplementedError


class GetTraining(RocService):
    @classmethod
    def run_service(
            roc: RocWebHandler = None,
            settings: UserSettings = None,
            custom_settings: dict = None
            ) -> bool:
        raise NotImplementedError


class GetArmory(RocService):
    @classmethod
    def run_service(
            roc: RocWebHandler = None,
            settings: UserSettings = None,
            custom_settings: dict = None
            ) -> bool:
        raise NotImplementedError


class GetAccount(RocService):
    """Gets a ROC Account with gold, stats, training and armory"""

    @classmethod
    def run_service(
            roc: RocWebHandler = None,
            settings: UserSettings = None,
            custom_settings: dict = None
            ) -> bool:
        raise NotImplementedError
