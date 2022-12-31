import abc

import rocalert.models.pages.genericpages as gp


class PageGenerationException(Exception):
    pass


class ROCPageGeneratorABC(abc.ABC):
    @abc.abstractmethod
    def generate(self, pagehtml: str) -> gp.RocPage:
        msg = f'{self.__class__.__name__} is an ABC'
        raise NotImplementedError(msg)
