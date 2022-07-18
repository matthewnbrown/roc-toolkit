from twocaptcha import TwoCaptcha, TimeoutException
from twocaptcha.api import ApiException, NetworkException
from rocalert.roc_settings.settingstools import UserSettings
from rocalert.roc_web_handler import RocWebHandler
from rocalert.roc_web_handler import Captcha
from rocalert.services.rocservice import RocService


class AutoCaptchaService(RocService):
    """Service that uses 2Captcha for captcha solving"""
    def __is_twocpatch_key_invalid(self, twocaptcha_key):
        return twocaptcha_key is None or len(twocaptcha_key) == 0

    def __create_solver(self, key: str) -> TwoCaptcha:
        solver = TwoCaptcha(key)
        return solver

    def __twocaptcha_solve(self, api_key, img_path) -> str:
        ans = None
        response = None
        if self.__is_twocaptcha_key_invalid():
            return {
                'ans': ans,
                'error': 'ERROR_TWOCAPTCHA_KEY_NOT_SET',
                'response': response}

        try:
            solver = self.__create_solver(key=api_key)
            hinttext = 'Single digit between 1-9  (1, 2, 3, 4, 5, 6, 7, 8, 9)'
            response = solver.normal(img_path, hintText=hinttext)
            ans = response['code']
            error = None
        except ApiException as exception:
            error = f'Exception: {exception.args[0]}'
            if 'ZERO_BALANCE' in exception.args[0]:
                error = f'Critical Exception: {exception.args[0]}'
        except NetworkException as exception:
            error = f'Exception: {exception.args[0]}'
        except TimeoutException as exception:
            error = f'Exception: {exception.args[0]}'

        return {'ans': ans, 'response': response, 'error': error}

    """Runs the service"""
    def run_service(
            self,
            roc: RocWebHandler = None,
            settings: UserSettings = None,
            custom_settings: dict = None
            ) -> bool:
        if 'captcha' not in custom_settings:
            return {'error': 'captcha not in custom settings'}
        captcha = custom_settings['captcha']
        if captcha is None:
            return {'error': 'No captcha supplied in request'}
        elif captcha.img is None:
            return {'error': 'Captcha.img not supplied in request'}

        if 'api_key' not in custom_settings:
            return {'error': 'No api_key supplied in request'}

        api_key = custom_settings['api_key']
        # TODO: SAVE IMAGE
        return self.__twocaptcha_solve(api_key, captcha.img)
