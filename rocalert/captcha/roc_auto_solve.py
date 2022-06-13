from twocaptcha import TwoCaptcha # pip install 2captcha-python
from twocaptcha import api
from rocalert.captcha.pyrocaltertgui import get_user_answer_captcha

def Solve(api_key, imgpath) -> str:
    solver = TwoCaptcha(api_key)
    try:
        result = solver.normal(imgpath, numeric = 1, min_len = 1, max_len = 1)['code']
    except api.ApiException as e:
        result = e.args[0]
    except api.NetworkException as e:
        result = e.args[0]
    except api.TimeoutException as e:
        result = e.args[0]
    except api.ValidationException as e:
        result = e.args[0]

    return result

class ROCCaptchaSolver:
    def __init__(self) -> None:
        self.twocaptcha_key = None

    def __is_twocaptcha_key_invalid(self):
        return self.twocaptcha_key is None or len(self.twocaptcha_key) == 0

    def set_twocaptcha_apikey(self, key: str) -> None:
        self.twocaptcha_key = key
        self.solver = TwoCaptcha(self.twocaptcha_key)

    def twocaptcha_solve(self, img_path) -> str:
        if self.__is_twocaptcha_key_invalid():
            return "ERROR_TWOCAPTCHA_KEY_NOT_SET"
        try:
            self.last_twocaptcha = self.solver.normal(img_path, numeric = 1, min_len = 1, max_len = 1)
            result = self.last_twocaptcha['code']
        except api.ApiException as e:
            result = e.args[0]
        except api.NetworkException as e:
            result = e.args[0]
        except api.TimeoutException as e:
            result = e.args[0]
        except api.ValidationException as e:
            result = e.args[0]

        return result

    def report_last_twocaptcha(self, wascorrect):
        if self.__is_twocaptcha_key_invalid():
            return

        try:
            self.solver.report(self.last_twocaptcha['captchaId'], wascorrect)
        except (api.NetworkException, api.ApiException) as e:
            print('Error reporting captcha: {}'.format(e.args[0]))

    def gui_solve(self, img):
        return get_user_answer_captcha(img)
    