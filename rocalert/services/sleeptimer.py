import abc
import datetime

from rocalert.roc_settings import UserSettings


class SleepTimerABC(abc.ABC):
    def sleep():
        raise NotImplementedError("SleepTimerABC is an abstract class")


class SleepTimer(SleepTimerABC):
    def __init__(self, user_settings: UserSettings) -> None:
        self._usersettings = user_settings

    def _in_nightmode(self) -> bool:
        if not self._usersettings.use_nightmode:
            return False
        start, end = self._usersettings.nightmode_activetime_range
        now = datetime.datetime.now().time()

        if start <= end:
            innightmode = start <= now <= end
        else:
            innightmode = start <= now or now <= end

        return innightmode

    def _calculate_nightmode_sleeptime(self) -> float:
        pass

    def _calculate_regular_sleeptime(self) -> float:
        pass

    def sleep():
        pass
