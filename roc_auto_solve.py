from twocaptcha import TwoCaptcha # pip install 2captcha-python

def Solve(api_key, imgpath):
    solver = TwoCaptcha(api_key)
    result = solver.normal(imgpath, numeric = 1, min_len = 1, max_len = 1)
    return result