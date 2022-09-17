from rocalert.roc_settings.settingstools import UserSettings
from rocalert.roc_web_handler import RocWebHandler
from rocalert.services.autocaptchaservice import AutoCaptchaService
from rocalert.services.rocservice import RocService
from rocalert.rocpurchases.roc_buyer import ROCTrainer


class RocTrainerService(RocService):
    """Service to generate soldier training payload"""

    @classmethod
    def run_service(
            cls,
            roc: RocWebHandler = None,
            settings: UserSettings = None,
            custom_settings: dict = None
            ) -> dict:
        r, e = 'response', 'error'

        missingparams = cls.__check_params(roc, settings, custom_settings)
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

        captcha = roc.get_img_captcha(roc.Pages.TRAINER)
        payload = trainer.create_order_payload(gold)

        if settings.auto_solve_captchas():
            captcha = AutoCaptchaService.run_service() # TODO: Write params

        roc.submit_captcha(captcha, captcha.ans, roc.Pages.TRAINER, payload)


        return {r: 'success', 'result': payload}
