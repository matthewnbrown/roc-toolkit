import abc
import datetime
import random
import typing

from rocalert.roc_settings import UserSettings


class SleepTimerException(Exception):
    pass


class SleepTimerABC(abc.ABC):
    def calculate_sleeptime():
        raise NotImplementedError("SleepTimerABC is an abstract class")


class SleepTimer(SleepTimerABC):
    def __init__(
            self,
            user_settings: UserSettings,
            randomlowhigh: typing.Callable[[float, float], float] = None,
            current_time_getter: typing.Callable[[], datetime.datetime] = None,
            max_postnightmode_sleeptime_mins: int = None
            ) -> None:
        self._usersettings = user_settings

        if randomlowhigh is None:
            randomlowhigh = random.uniform
        if current_time_getter is None:
            current_time_getter = datetime.datetime.now
        if max_postnightmode_sleeptime_mins is None:
            min_regtime, _ = user_settings.regular_waittimes_seconds
            max_postnightmode_sleeptime_mins = min_regtime // 60

        self._randomfunc = randomlowhigh
        self._current_time = current_time_getter
        self._max_postnightmode_naptime_mins = max_postnightmode_sleeptime_mins

    def time_is_in_nightmode(self, time: datetime.datetime) -> bool:
        if not self._usersettings.use_nightmode:
            return False
        start, end = self._usersettings.nightmode_activetime_range
        _time = time.time()
        if start <= end:
            innightmode = start <= _time <= end
        else:
            innightmode = start <= _time or _time <= end

        return innightmode

    def in_nightmode(self) -> bool:
        if not self._usersettings.use_nightmode:
            return False
        now = self._current_time()
        return self.time_is_in_nightmode(now)

    def _calculate_random(self, mintime, maxtime) -> float:
        if mintime > maxtime:
            mintime, maxtime = maxtime, mintime

        return mintime + int(self._randomfunc(0, 1) * (maxtime - mintime))

    def _calculate_nightmode_sleeptime(self) -> float:
        _, nightmode_end = self._usersettings.nightmode_activetime_range
        mintime, maxtime = self._usersettings.nightmode_waittime_range

        waittime_mins = self._calculate_random(mintime, maxtime)
        waittime = datetime.timedelta(minutes=waittime_mins)
        now = self._current_time()

        sleep_overflows_waketime = not self.time_is_in_nightmode(now+waittime)
        if sleep_overflows_waketime:
            today_end = datetime.datetime.combine(now.date(), nightmode_end)

            if now < today_end:
                end_date = today_end
            else:
                end_date = datetime.datetime.combine(
                    (now + datetime.timedelta(days=1)).date(), nightmode_end)

            waittime_mins = (end_date - now).total_seconds()//60 + \
                self._randomfunc(0, self._max_postnightmode_naptime_mins)

        if (mintime > waittime_mins and not sleep_overflows_waketime
                or maxtime < waittime_mins):
            msg = ("Nightmode sleep time fell out of range: "
                   + f"{mintime} <= {waittime_mins} <= {maxtime}")
            raise SleepTimerException(msg)

        return waittime_mins * 60

    def _calculate_regular_sleeptime(self) -> float:
        mintime, maxtime = self._usersettings.regular_waittimes_seconds
        sleeptime = self._calculate_random(mintime, maxtime)

        if sleeptime > maxtime or sleeptime < mintime:
            msg = ("Regular sleep time fell out of range: "
                   + f"{mintime} <= {sleeptime} <= {maxtime}")
            raise SleepTimerException(msg)

        return sleeptime

    def calculate_sleeptime(self):
        if self.in_nightmode():
            sleeptime = self._calculate_nightmode_sleeptime()
        else:
            sleeptime = self._calculate_regular_sleeptime()

        return sleeptime
