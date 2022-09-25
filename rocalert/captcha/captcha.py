from abc import abstractmethod, abstractproperty


class RocCaptcha:
    def __init__(self) -> None:
        super().__init__()
        self._answer = None
        self._payload = None

    @property
    def is_solved(self) -> bool:
        return self._answer is not None

    @abstractproperty
    def answer(self):
        raise NotImplementedError

    @answer.setter
    def answer(self, new_answer) -> None:
        raise NotImplementedError

    @abstractmethod
    def get_payload(self):
        raise NotImplementedError


class ImageCaptcha(RocCaptcha):
    def __init__(self) -> None:
        super().__init__()

    def get_payload(self):
        return super().get_payload()


class EquationCaptcha(RocCaptcha):
    def __init__(self) -> None:
        super().__init__()

    def get_payload(self):
        return super().get_payload()


class TextCaptcha(RocCaptcha):
    def __init__(self) -> None:
        super().__init__()
