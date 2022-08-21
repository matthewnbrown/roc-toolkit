from rocalert.roc_settings.settingstools import UserSettings
from rocalert.roc_web_handler import RocWebHandler


class RocService():
    """Generic class for a ROC service"""

    """Runs the service"""
    def run_service(
            self,
            roc: RocWebHandler = None,
            settings: UserSettings = None,
            custom_settings: dict = None
            ) -> bool:
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
        if 'trainer_settings' not in custom_settings:
            return {r: 'failure',
                    e: '\'trainer_settings\' not passed in request'}
        if custom_settings['trainer_settings'] is None:
            return {r: 'failure', e: '\'trainer_settings\' is none'}
        if not roc.is_logged_in():
            return {r: 'failure', e: 'ROC session not logged in'}

        return {r: 'failure', e: 'Not implemented'}
