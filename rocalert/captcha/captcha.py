from abc import abstractproperty
from random import random
from typing import Dict

from rocalert.roc_web_handler import Captcha



class RocCaptcha:
    def __init__(self, answer, correct: bool = None) -> None:
        self._answer = answer
        self._correct = correct

    @property
    def is_solved(self) -> bool:
        return self._answer is not None

    @abstractproperty
    def answer(self):
        raise NotImplementedError

    @answer.setter
    def answer(self, new_answer) -> None:
        raise NotImplementedError

    @property
    def correct(self) -> bool:
        return self._correct

    @correct.setter
    def correct(self, iscorrect: bool) -> None:
        self._correct = iscorrect


class ImageCaptcha(RocCaptcha):
    def __init__(
            self, hash: str, image: bytes = None,
            answer: str = None, correct: bool = None,
            page: str = None
            ) -> None:
        super().__init__(answer, correct)

        self._hash = hash
        self._image = image
        self._page = page

    @property
    def image(self) -> bytes:
        return self._image

    @image.setter
    def image(self, image: bytes) -> None:
        self._image = image

    @property
    def answer(self) -> str:
        return self._answer

    @answer.setter
    def answer(self, newans: str) -> None:
        self._answer = newans

    @property
    def page(self) -> str:
        return self._page

    @page.setter
    def page(self, newpage) -> str:
        self._page = newpage


class EquationCaptcha(RocCaptcha):
    def __init__(
                self,
                equation: str, answer: str = None,
                correct: bool = None) -> None:
        super().__init__(answer, correct)

    @property
    def answer(self) -> str:
        return self.answer

    @answer.setter
    def answer(self, newans: int) -> None:
        self.answer = str(newans)


class TextCaptcha(RocCaptcha):
    def __init__(
            self, hash: str, image: bytes = None,
            answer: str = None, correct: bool = None
            ) -> None:
        super().__init__(answer, correct)
        self._hash = hash
        self._image = image

    @property
    def image(self) -> bytes:
        return self._image

    @image.setter
    def image(self, image: bytes) -> None:
        self._image = image

    @property
    def answer(self) -> str:
        return self._answer

    @answer.setter
    def answer(self, newans: str) -> None:
        self._answer = newans


class ROCCaptchaSelector():
    __btn_dimensions = (40, 30)
    __keypadTopLeft = {'roc_recruit': [890, 705],
                       'roc_armory': [973, 1011],
                       'roc_attack': [585, 680],
                       'roc_spy': [585, 695]}
    __keypadGap = [52, 42]

    def __init__(self, resolution=None) -> None:
        self.resolution = resolution

    def get_xy(self, number):
        pass

    def get_xy_static(self, number, page):
        if page not in self.__keypadTopLeft:
            raise Exception(
                f'Page {page} does not have coordinates for captchas!'
                )
        number = int(number) - 1
        x_btn = self.__keypadTopLeft[page][0] \
            + (number % 3) * self.__keypadGap[0]
        y_btn = self.__keypadTopLeft[page][1] \
            + (number // 3) * self.__keypadGap[1]

        x_click = -x_btn
        while x_click < x_btn or x_click > x_btn + self.__btn_dimensions[0]:
            x_click = x_btn + random.normal(0, self.__btn_dimensions[0]/3)
        y_click = -y_btn
        while y_click < y_btn or y_click > y_btn + self.__btn_dimensions[1]:
            y_click = y_btn + random.normal(0, self.__btn_dimensions[1]/3)

        return (int(x_click), int(y_click))


class CaptchaPayloadGenerator:
    @classmethod
    def generate(cls, captcha: RocCaptcha) -> Dict[str, str]:
        if type(captcha) == ImageCaptcha:
            return cls._gen_image_payload(captcha)
        if type(captcha) == EquationCaptcha:
            return cls._gen_eqn_payload(captcha)
        if type(captcha) == TextCaptcha:
            return cls._gen_textcap_payload(captcha)

    @classmethod
    def _gen_image_payload(cls, captcha: ImageCaptcha) -> Dict[str, str]:
        pass

    @classmethod
    def _gen_eqn_payload(cls, captcha: Captcha) -> Dict[str, str]:
        pass

    @classmethod
    def _gen_textcap_payload(cls, captcha: Captcha) -> Dict[str, str]:
        return {}