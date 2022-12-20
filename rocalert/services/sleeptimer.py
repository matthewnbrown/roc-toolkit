import abc
import datetime
import time
import random
import typing

from rocalert.roc_settings import UserSettings


class SleepTimerException(Exception):
    pass


class SleepTimerABC(abc.ABC):
    def sleep():
        raise NotImplementedError("SleepTimerABC is an abstract class")


class SleepTimer(SleepTimerABC):
    def __init__(
            self,
            user_settings: UserSettings,
            randomlowhigh: typing.Callable[[float, float], float] = None,
            current_time_getter: typing.Callable[[], datetime.datetime] = None
            ) -> None:
        self._usersettings = user_settings

        if randomlowhigh is None:
            randomlowhigh = random.uniform
        if current_time_getter is None:
            current_time_getter = datetime.datetime.now

        self._randomfunc = randomlowhigh
        self._current_time = current_time_getter

    def time_is_in_nightmode(self, time: datetime.datetime) -> bool:
        if not self._usersettings.use_nightmode:
            return False
        start, end = self._usersettings.nightmode_activetime_range
        if start <= end:
            innightmode = start <= time <= end
        else:
            innightmode = start <= time or time <= end

        return innightmode

    def in_nightmode(self) -> bool:
        if not self._usersettings.use_nightmode:
            return False
        now = self._current_time()
        return self.time_is_in_nightmode(now)

    def _calculate_random(self, mintime, maxtime) -> float:
        if mintime > maxtime:
            mintime, maxtime = maxtime, mintime

        mintime + int(self._randomfunc(0, 1) * (maxtime - mintime))

    def _calculate_nightmode_sleeptime(self) -> float:
        _, nightmode_end = self._usersettings.nightmode_activetime_range
        mintime, maxtime = self._usersettings.nightmode_waittime_range

        waittime_secs = 60*self._calculate_random(mintime, maxtime)
        waittime = datetime.timedelta(seconds=waittime_secs)
        now = self._current_time()

        if not self.time_is_in_nightmode(now+waittime):
            today_end = datetime.datetime.combine(now.date, nightmode_end)

            if now < today_end:
                end_date = today_end
            else:
                end_date = datetime.datetime.combine(
                    (now + datetime.timedelta(days=1)).date, nightmode_end)

            waittime = (end_date - now).total_seconds + self._randomfunc(5)*60

    def _calculate_regular_sleeptime(self) -> float:
        mintime = self._usersettings['min_checktime_secs']
        maxtime = self._usersettings['max_checktime_secs']

        return self._calculate_random(mintime, maxtime)

    def sleep(self):
        if self.in_nightmode():
            sleeptime = self._calculate_nightmode_sleeptime()
        else:
            sleeptime = self._calculate_regular_sleeptime()

        time.sleep(sleeptime)
