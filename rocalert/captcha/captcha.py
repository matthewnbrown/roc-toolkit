from abc import ABC, abstractmethod


class RocCaptcha(ABC):
    def __init__(self) -> None:
        super().__init__()

    @abstractmethod
    def get_payload(self):
        raise NotImplementedError('get_payload is not implemented')


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
