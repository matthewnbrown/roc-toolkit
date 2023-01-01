import abc

import rocalert.models.pages.genericpages as gp


class PageGenerationException(Exception):
    pass


class ROCPageGeneratorABC(abc.ABC):
    @abc.abstractmethod
    def generate() -> gp.RocPage:
        msg = 'ROCPageGeneratorABC is an ABC'
        raise NotImplementedError(msg)
