from .manualcaptchasolver import manual_captcha_solve
from .truecaptchasolver import TrueCaptchaSolver
from .twocaptchasolver import TwoCaptchaSolver

if __name__ == "__main__":
    manual_captcha_solve()
    TwoCaptchaSolver()
    TrueCaptchaSolver()
