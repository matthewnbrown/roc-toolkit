from twocaptcha import TwoCaptcha, TimeoutException
from twocaptcha.api import ApiException, NetworkException
from rocalert.roc_settings.settingstools import UserSettings
from rocalert.roc_web_handler import RocWebHandler
from rocalert.services.rocservice import RocService
import PIL.Image
import io


class AutoCaptchaService(RocService):
    """Service that uses 2Captcha for captcha solving"""
    @classmethod
    def __is_twocaptcha_key_invalid(cls, twocaptcha_key):
        return twocaptcha_key is None or len(twocaptcha_key) == 0

    @classmethod
    def __create_solver(cls, key: str) -> TwoCaptcha:
        solver = TwoCaptcha(key)
        return solver

    @classmethod
    def __twocaptcha_solve(cls, api_key, img_path) -> str:
        ans = None
        response = None
        if self.__is_twocaptcha_key_invalid():
            return {
                'answer': ans,
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

        return {'answer': ans, 'response': response, 'error': error}

        """_summary_
        Uses 2captcha to solve a given captcha

        requires:
            settings: Must contain 'auto_captcha_key' which contains an api key
            custom_settings: Must contain 'captcha' which contains an img

        returns:
            dictionary that potentially contains:
                'error': Describes any error that occurred
                'answer': Any answer received from service
                'response': The entire response from 2captcha
        """
    @classmethod
    def run_service(
            cls,
            roc: RocWebHandler = None,
            settings: UserSettings = None,
            custom_settings: dict = None
            ) -> bool:
        if settings is None:
            return {'error': 'No user settings supplied in request'}
        api_key = settings.get_value('auto_captcha_key')
        if api_key is None or len(api_key) == 0:
            {'error': 'Bad captcha api key.'}
        if 'captcha' not in custom_settings:
            return {'error': 'captcha not in custom settings'}
        captcha = custom_settings['captcha']
        if captcha is None:
            return {'error': 'No captcha supplied in request'}
        elif captcha.img is None:
            return {'error': 'Captcha.img not supplied in request'}

        img = PIL.Image.open(io.BytesIO(captcha.img))
        path = settings['captcha_save_path'] + captcha.hash + '.png'
        img.save(path)
        return cls.__twocaptcha_solve(api_key, captcha.img)

        """_summary_
        Reports a captcha answer as correct/incorrect to 2captcha service

        requires:
            settings:
                Must contain 'auto_captcha_key' which contains an api key
            response:
                Received after calling run_service
            wascorrect:
                Validity of the answer to the captcha
        """
    @classmethod
    def report_captcha(
            cls,
            settings: UserSettings,
            response: dict,
            wascorrect: bool
            ) -> str:
        if settings is None:
            return {'error': 'No user settings supplied in request'}
        api_key = settings.get_value('auto_captcha_key')
        if api_key is None or len(api_key) == 0:
            {'error': 'Bad captcha api key.'}

        if response is None:
            return {'error': 'No captcha service response supplied'}

        result = 'success'
        try:
            solver = cls.__create_solver(key=api_key)
            solver.report(response['captchaId'], wascorrect)
        except (NetworkException, ApiException) as e:
            result = 'Error reporting captcha: {}'.format(e.args[0])
        return result
