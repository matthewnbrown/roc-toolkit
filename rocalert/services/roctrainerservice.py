from rocalert.roc_settings.settingstools import UserSettings
from rocalert.roc_web_handler import RocWebHandler
from rocalert.services.rocservice import RocService
from rocalert.rocpurchases.roc_buyer import ROCTrainer


class RocTrainerService(RocService):
    """Service to generate soldier training payload"""

    """Runs the service"""
    def run_service(
            self,
            roc: RocWebHandler = None,
            settings: UserSettings = None,
            custom_settings: dict = None
            ) -> bool:
        r, e = 'response', 'error'

        missingparams = self.__check_params(roc, settings, custom_settings)
        if missingparams:
            return missingparams

        if 'trainer_settings' not in custom_settings:
            return {r: 'failure',
                    e: '\'trainer_settings\' not passed in request'}
        if custom_settings['trainer_settings'] is None:
            return {r: 'failure', e: '\'trainer_settings\' is none'}
        if not roc.is_logged_in():
            return {r: 'failure', e: 'ROC session not logged in'}

        trainer = ROCTrainer(roc, custom_settings['trainer_settings'])
        gold = roc.current_gold()
        if not trainer.purchase_required(gold):
            return {r: 'failure', e: 'Purchase not required'}

        payload = trainer.create_order_payload(gold)

        return {r: 'success', 'result': payload}
