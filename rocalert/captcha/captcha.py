from abc import abstractmethod, abstractproperty
from typing import Dict


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
            answer: str = None, correct: bool = None
            ) -> None:
        super().__init__(answer, correct)

        self._hash = hash
        self._image = image
        self._answer = answer
        self._correct = correct

    @property
    def image(self) -> bytes:
        return self._image

    @image.setter
    def image(self, image: bytes) -> None:
        self._image = image

    @property
    def answer(self) -> bytes:
        return self._answer

    @answer.setter
    def answer(self, newans: bytes) -> None:
        self._answer = newans


class EquationCaptcha(RocCaptcha):
    def __init__(self) -> None:
        super().__init__()


class TextCaptcha(RocCaptcha):
    def __init__(self) -> None:
        super().__init__()
