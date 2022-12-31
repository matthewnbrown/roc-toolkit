import datetime as dt
import dataclasses

import rocalert.enums as rocenums


@dataclasses.dataclass
class Captcha:
    captcha_type: rocenums.CaptchaType
    expiration_date: dt.datetime
    creation_date: dt.datetime
    answer: str
    answer_correct: bool


@dataclasses.dataclass
class ImageCaptcha(Captcha):
    image_hash: str
    image: bytes


@dataclasses.dataclass
class TextCaptcha(Captcha):
    image_hash: str
    image: bytes


@dataclasses.dataclass
class EquationCaptcha(Captcha):
    equation: str
