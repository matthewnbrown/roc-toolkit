from requests import Response
from rocalert.roc_web_handler import Captcha


class GetCaptchaService:
    @classmethod
    def run_service(cls, response: Response) -> Captcha:
        """_summary_

        Args:
            page_text (str): _description_
                Response text from the page where the captcha is located

        Returns:
            Captcha: _description_
                Captcha pulled from page.
                Will be None if no captcha is detected
        """
        captcha_type = cls._detectcaptchatype(response)

        if captcha_type is None:
            return None

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
