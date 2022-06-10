from twocaptcha import TwoCaptcha, ApiException, NetworkException,TimeoutException,ValidationException # pip install 2captcha-python
from twocaptcha import api
def Solve(api_key, imgpath) -> str:
    solver = TwoCaptcha(api_key)
    try:
        result = solver.normal(imgpath, numeric = 1, min_len = 1, max_len = 1)['code']
        success = True
    except api.ApiException as e:
        result = e.args[0]
    except NetworkException as e:
        result = e.args[0]
    except TimeoutException as e:
        result = e.args[0]
    except ValidationException as e:
        result = e.args[0]

    return result