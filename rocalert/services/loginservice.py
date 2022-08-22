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
        r, e = 'result', 'error'
        if roc is None:
            return {r: 'failure', e: 'roc session not passed in request'}
        if settings is None:
            return {r: 'failure', e: 'User settings not passed in request'}
        if custom_settings is None:
            return {r: 'failure', e: 'No custom settings passed in request'}
        if 'site_settings' not in custom_settings:
            return {r: 'failure', e: '\'site_settings\' not passed in request'}
        if custom_settings['site_settings'] is None:
            return {r: 'failure', e: '\'site_settings\' is none'}
        if roc.is_logged_in():
            return {r: 'failure', e: 'ROC session already logged in'}

        repeated_failures = 0

        while repeated_failures < 3:
            res = roc.detailed_login(
                settings.get_value('email'),
                settings.get_value('password'))

            if 'success' in res:
                return {r: 'success', e: None}
            if 'incorrect_login' in res:
                return {r: 'failure', e: 'Incorrect login'}
            if 'general_failure' in res:
                repeated_failures += 1
        return {r: 'failure', e: 'Critical error: Too many failure attempts'}
