from time import time
from twocaptcha import TwoCaptcha, TimeoutException
from twocaptcha.api import ApiException, NetworkException
from rocalert.captcha.pyrocaltertgui import get_user_answer_captcha


def Solve(api_key, imgpath) -> str:
    solver = TwoCaptcha(api_key)
    try:
        resp = solver.normal(imgpath, numeric=1, min_len=1, max_len=1)
        result = resp['code']
    except ApiException as exception:
        result = exception.args[0]
    except NetworkException as exception:
        result = exception.args[0]
    except TimeoutException as exception:
        result = exception.args[0]

    return result


class ROCCaptchaSolver:
    def __init__(self) -> None:
        self.twocaptcha_key = None

    def __is_twocaptcha_key_invalid(self):
        return self.twocaptcha_key is None or len(self.twocaptcha_key) == 0

    def set_twocaptcha_apikey(self, key: str, solver=None) -> None:
        self.twocaptcha_key = key

        if solver:
            self.solver = solver
        else:
            self.solver = TwoCaptcha(self.twocaptcha_key)

    def twocaptcha_solve(self, img_path) -> str:
        if self.__is_twocaptcha_key_invalid():
            return "ERROR_TWOCAPTCHA_KEY_NOT_SET"
        try:
            hinttext = 'Single digit between 1-9  (1, 2, 3, 4, 5, 6, 7, 8, 9)'
            self.last_twocaptcha = \
                self.solver.normal(img_path, hintText=hinttext)
            result = self.last_twocaptcha['code']
        except ApiException as exception:
            result = str(exception.args[0])
            if 'NO_SLOT' in result:
                print('No slot Twocaptcha slot available, \
                    trying again in 5 seconds')
                time.sleep(5)
            elif 'ZERO_BALANCE' in result:
                print("ERROR: Received response \'{}\'!\n\
                    Check your 2captcha balance!\nExiting...".format(result))
                quit()
        except NetworkException as exception:
            print("Twocaptcha network exception!")
            result = str(exception.args[0])
        except TimeoutException as exception:
            print("Twocaptcha timeout exception!")
            result = str(exception.args[0])

        return result

    def report_last_twocaptcha(self, wascorrect):
        if self.__is_twocaptcha_key_invalid():
            return

        try:
            self.solver.report(self.last_twocaptcha['captchaId'], wascorrect)
        except (NetworkException, ApiException) as e:
            print('Error reporting captcha: {}'.format(e.args[0]))

    def gui_solve(self, img):
        return get_user_answer_captcha(img)
