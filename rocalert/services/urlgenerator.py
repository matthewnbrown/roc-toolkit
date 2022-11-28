import abc


class URLNotFoundError(Exception):
    pass


class ROCUrlGeneratorABC(abc.ABC):
    def get_page_url(page: str) -> str:
        raise NotImplementedError()


class ROCDecryptUrlGenerator(ROCUrlGeneratorABC):
    def __init__(self) -> None:
        pass

    def get_page_url(page: str) -> str:
        pass


class ROCSiteSettingsUrlGenerator(ROCUrlGeneratorABC):
    def __init__(self, sitesettings) -> None:
        self._sitesettings = sitesettings

    def get_page_url(page: str) -> str:
        raise NotImplementedError()