from ...roc_web_handler import Captcha
from twocaptcha import TwoCaptcha, TimeoutException
from twocaptcha.api import ApiException, NetworkException
from rocalert.roc_settings import UserSettings
from rocalert.services.rocservice import RocService
import PIL.Image
import io

def twocaptcha_captcha_solve(
        solver: TwoCaptcha, captcha: Captcha, savepath: str):
    img = PIL.Image.open(io.BytesIO(captcha.img))
    path = savepath + captcha.hash + '.png'
    img.save(path)

    hinttext = 'Single digit between 1-9  (1, 2, 3, 4, 5, 6, 7, 8, 9)'
    response = solver.normal(path, hintText=hinttext)
    ans = response['code']


def report_twocaptcha_answer(solver: TwoCaptcha, response):
    try:
        solver.report(response['captchaId'], wascorrect)
    except (NetworkException, ApiException) as e:
        result = 'Error reporting captcha: {}'.format(e.args[0])
    return result