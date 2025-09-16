import abc
import io
import json
import os
from typing import Optional

import PIL.Image
from requests import Response

from rocalert.captcha.solvers.rocapicaptchasolver import RocApiCaptchaSolver
from rocalert.roc_web_handler import Captcha, RocWebHandler

from ..captcha.solvers import TrueCaptchaSolver, TwoCaptchaSolver, manual_captcha_solve


class CaptchaSolveException(Exception):
    pass


class CaptchaReportException(Exception):
    pass


class GetCaptchaService:
    @classmethod
    def run_service(cls, response: Response, roc: RocWebHandler) -> Captcha:
        """_summary_
            Retrieves a captcha from a page
        Args:
            page_text (str): _description_
                Response text from the page where the captcha is located
        Raises:
            Exception: _description_
                ROC is None
            Exception: _description_
                response is None
        Returns:
            Captcha: _description_
                Captcha pulled from page.
                Will be None if no captcha is detected..
        """

        if roc is None:
            raise Exception("ROC parameter must exist")
        elif response is None:
            raise Exception("Response parameter must exist")

        captcha_type = cls._detectcaptchatype(response)

        if captcha_type == Captcha.CaptchaType.IMAGE:
            return cls._get_img_captcha(response)
        if captcha_type == Captcha.CaptchaType.EQUATION:
            return cls._get_equation_captcha(response)
        if captcha_type == Captcha.CaptchaType.TEXT:
            return cls._get_text_captcha(response)

        return None

    @classmethod
    def _get_img_hash(cls, pagetext: str) -> str:
        index = pagetext.find("img.php?hash=")
        if index == -1:
            return None
        endIndex = pagetext.find('"', index, index + 100)
        imghash = pagetext.text[index + len("img.php?hash=") : endIndex]
        return imghash

    @classmethod
    def _get_img_captcha(cls, resp: Response, roc: RocWebHandler) -> Captcha:
        imghash = cls._get_img_hash(resp.text)
        imgbytes = roc.get_imgcap_from_hash(imghash)
        return Captcha(imghash, imgbytes, captype=Captcha.CaptchaType.IMAGE)

    @classmethod
    def _get_equation_captcha(cls, resp: Response) -> Captcha:
        index = resp.text.find("<h1>What is")
        if index == -1:
            return None
        endIndex = resp.text.find("</h1>", index, index + 100)
        equation = resp.text[index + len("<h1>What is") : endIndex]
        equation = equation.strip()[:-1]
        return Captcha(equation, captype=Captcha.CaptchaType.EQUATION)

    @classmethod
    def _get_text_captcha(cls, resp: Response, roc: RocWebHandler) -> Captcha:
        return Captcha("TEXT", captype=Captcha.CaptchaType.TEXT)

    @classmethod
    def _has_text_cap(cls, response: Response) -> bool:
        return "cooldown" in response.url

    @classmethod
    def _has_img_cap(cls, response: Response) -> bool:
        return "[click the correct number to proceed]" in response.text

    @classmethod
    def _has_equation_cap(cls, response: Response) -> bool:
        return "<h1>What is" in response.text

    @classmethod
    def _detectcaptchatype(cls, response: Response) -> Captcha.CaptchaType:
        if cls._has_text_cap(response):
            return Captcha.CaptchaType.TEXT
        if cls._has_img_cap(response):
            return Captcha.CaptchaType.IMAGE
        if cls._has_equation_cap(response):
            return Captcha.CaptchaType.EQUATION
        return None


def get_captcha_settings(captchaservice: str) -> Optional[dict]:
    if captchaservice in ["2captcha", "twocaptcha"]:
        filename = "2captcha_settings.json"
    elif captchaservice in ["truecaptcha", "true captcha"]:
        filename = "truecaptcha_settings.json"
    elif captchaservice in ["rocapi", "ai"]:
        filename = "rocapi_settings.json"
    else:
        return None

    if os.path.isfile(filename):
        with open(filename, "r") as f:
            return json.loads(f.read())

    return None


def create_captcha_settings_file(captchaservice: str) -> None:
    if captchaservice in ["2captcha", "twocaptcha"]:
        filename = "2captcha_settings.json"
        settings = {
            "apiKey": "somekey",
        }
    elif captchaservice in ["truecaptcha", "true captcha"]:
        filename = "truecaptcha_settings.json"

        settings = {
            "userId": "someuserid",
            "apiKey": "somekey",
            "mode": "auto",
        }
    elif captchaservice in ["rocapi", "ai"]:
        filename = "rocapi_settings.json"
        settings = {
            "base_url": "http://localhost:8001",
            "solve_url": "/api/v1/solve",
            "report_url": "/api/v1/feedback"
        }

    with open(filename, "w") as f:
        f.write(json.dumps(settings, indent=4))

    return filename


class CaptchaSolverServiceABC(abc.ABC):
    @abc.abstractmethod
    def solve_captcha(self, captcha: Captcha) -> Captcha:
        raise NotImplementedError

    @abc.abstractmethod
    def report_captcha(self, captcha: Captcha) -> None:
        raise NotImplementedError


class ManualCaptchaSolverService(CaptchaSolverServiceABC):
    def solve_captcha(self, captcha: Captcha):
        if captcha is None:
            raise CaptchaSolveException("Captcha cannot be NoneType")
        elif captcha.img is None:
            raise CaptchaSolveException("Captcha cannot be NoneType")

        captcha = manual_captcha_solve(captcha)

        return captcha

    def report_captcha(self, captcha: Captcha) -> None:
        if captcha.ans_correct:
            print("Correct answer")
        else:
            print("Wrong answer")


class TwocaptchaSolverService(CaptchaSolverServiceABC):
    def __init__(self, api_key, savepath="captchas/") -> None:
        self._twocap = TwoCaptchaSolver(api_key, savepath=savepath)

    def solve_captcha(self, captcha: Captcha) -> Captcha:
        try:
            self._twocap.captcha_solve(captcha)
        except KeyboardInterrupt as e:
            raise e
        except Exception as e:
            raise CaptchaSolveException(f"Error: ${e}") from e

    def report_captcha(self, captcha: Captcha) -> None:
        try:
            self._twocap.report_answer(captcha)
        except KeyboardInterrupt as e:
            raise e
        except Exception as e:
            raise CaptchaReportException(f"Error: ${e}") from e


class TrueCaptchaSolverService(CaptchaSolverServiceABC):
    def __init__(
        self, userid: str, api_key: str, savepath="captchas/", mode="default"
    ) -> None:
        self._savepath = savepath
        self._truecap = TrueCaptchaSolver(userid, api_key, mode=mode)

    def solve_captcha(self, captcha: Captcha) -> Captcha:
        try:
            img = PIL.Image.open(io.BytesIO(captcha.img))
            path = f"{self._savepath}/{captcha.hash}.png"
            img.save(path)

            solver_result = self._truecap.solve(captcha)
            captcha.ans = solver_result["result"]
        except KeyboardInterrupt as e:
            raise e
        except Exception as e:
            raise CaptchaSolveException(f"Error: ${e}") from e

    def report_captcha(self, captcha: Captcha) -> None:
        try:
            self._truecap.report_answer(captcha)
        except KeyboardInterrupt as e:
            raise e
        except Exception as e:
            raise CaptchaReportException(f"Error: ${e}") from e

class RemoteCaptchaSolverService(CaptchaSolverServiceABC):
    def __init__(self, solve_url: str, report_url: str) -> None:
        self._rocapisolver = RocApiCaptchaSolver(solve_url, report_url)

    def solve_captcha(self, captcha: Captcha) -> Captcha:
        res = self._rocapisolver.solve(captcha)
        captcha.ans = res[0]
        return captcha

    def report_captcha(self, captcha: Captcha) -> None:
        self._rocapisolver.report(captcha.hash, captcha.ans_correct)

