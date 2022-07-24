from rocalert.roc_web_handler import RocWebHandler
from rocalert.services.rocservice import RocService
from rocalert.roc_settings.settingstools import UserSettings


class LoginService(RocService):
    """_summary_
    Attempts to login to ROC
    """
    def run_service(
            self,
            roc: RocWebHandler = None,
            settings: UserSettings = None,
            custom_settings: dict = None
            ) -> bool:
        """_summary_

        Args:
            roc (RocWebHandler, optional): ROC session used to login.
                Defaults to None.
            settings (UserSettings, optional): Settings file to use,
                must have username and password. Defaults to None.
            custom_settings (dict, optional): Must contain 'site_settings'
                Defaults to None.

        Returns:
            bool: Returns dictionary with:
                'result': 'success' or 'failure'
                'error': None if success, else general explanation of failure
        """
        pass
