from requests import Response
from rocalert.roc_web_handler import RocWebHandler
from rocalert.roc_web_handler import Captcha


class GetCaptchaService:
    @classmethod
    def run_service(cls, response: Response, roc: RocWebHandler) -> Captcha:
        """_summary_

        Args:
            page_text (str): _description_
                Response text from the page where the captcha is located

        Returns:
            Captcha: _description_
                Captcha pulled from page.
                Will be None if no captcha is detected
        """

        if roc is None:
            raise Exception('ROC parameter must exist')
        elif response is None:
            raise Exception('Response parameter must exist')

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
        index = pagetext.find('img.php?hash=')
        if index == -1:
            return None
        endIndex = pagetext.find('"', index, index+100)
        imghash = pagetext.text[index + len('img.php?hash='): endIndex]
        return imghash

    @classmethod
    def _get_img_captcha(cls, resp: Response, roc: RocWebHandler) -> Captcha:
        imghash = cls._get_img_hash(resp.text)
        imgbytes = roc.get_imgcap_from_hash(imghash)
        return Captcha(imghash, imgbytes, captype=Captcha.CaptchaType.IMAGE)

    @classmethod
    def _get_equation_captcha(cls, resp: Response) -> Captcha:
        index = resp.text.find('<h1>What is')
        if index == -1:
            return None
        endIndex = resp.text.find('</h1>', index, index+100)
        equation = resp.text[index + len('<h1>What is'):  endIndex]
        equation = equation.strip()[:-1]
        return Captcha(equation, captype=Captcha.CaptchaType.EQUATION)

    @classmethod
    def _get_text_captcha(cls, resp: Response, roc: RocWebHandler) -> Captcha:
        return Captcha('TEXT', captype=Captcha.CaptchaType.TEXT)

    @classmethod
    def _has_text_cap(cls, response: Response) -> bool:
        return 'cooldown' in response.url

    @classmethod
    def _has_img_cap(cls, response: Response) -> bool:
        return '[click the correct number to proceed]' in response.text

    @classmethod
    def _has_equation_cap(cls, response: Response) -> bool:
        return '<h1>What is' in response.text

    @classmethod
    def _detectcaptchatype(cls, response: Response) -> Captcha.CaptchaType:
        if cls._has_text_cap(response):
            return Captcha.CaptchaType.TEXT
        if cls._has_img_cap(response):
            return Captcha.CaptchaType.IMAGE
        if cls._has_equation_cap(response):
            return Captcha.CaptchaType.EQUATION
        return None
