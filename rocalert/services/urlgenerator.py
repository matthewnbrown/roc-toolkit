import abc

import rocalert.roc_settings as rocsettings


class URLNotFoundError(Exception):
    pass


class ROCUrlGenerator(abc.ABC):
    @abc.abstractmethod
    def get_page_url(self, page: str) -> str:
        raise NotImplementedError()

    @abc.abstractmethod
    def get_home() -> str:
        raise NotImplementedError()

    @abc.abstractmethod
    def get_armory() -> str:
        raise NotImplementedError()

    @abc.abstractmethod
    def get_training() -> str:
        raise NotImplementedError()

    @abc.abstractmethod
    def get_base() -> str:
        raise NotImplementedError()

    @abc.abstractmethod
    def get_recruit() -> str:
        raise NotImplementedError()


class ROCDecryptUrlGenerator(ROCUrlGenerator):
    def __init__(self) -> None:
        pass

    def get_page_url(page: str) -> str:
        pass


class ROCSiteSettingsUrlGenerator(ROCUrlGenerator):
    def __init__(self, sitesettings: rocsettings.SiteSettings) -> None:
        self._sitesettings = sitesettings

    def get_page_url(self, page: str) -> str:
        if page not in self._sitesettings.get_settings():
            raise URLNotFoundError(f'{page} url not known')

    def get_home(self) -> str:
        return self._sitesettings.get_home()

    def get_armory(self) -> str:
        return self._sitesettings.get_armory()

    def get_training(self) -> str:
        return self._sitesettings.get_training()

    def get_base(self) -> str:
        return self._sitesettings.get_home() + '/base.php'

    def get_recruit(self) -> str:
        return self._sitesettings.get_recruit()
