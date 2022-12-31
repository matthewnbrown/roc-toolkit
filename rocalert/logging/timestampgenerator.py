import abc
import datetime


class DateTimeGeneratorABC(abc.ABC):
    def get_current_time() -> datetime.datetime:
        msg = 'DateTimeGeneratorABC is not implemented'
        raise NotImplementedError(msg)


class DateTimeNowGenerator(DateTimeGeneratorABC):
    def get_current_time() -> datetime.datetime:
        return datetime.datetime.now()
