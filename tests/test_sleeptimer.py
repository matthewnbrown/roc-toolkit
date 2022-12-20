import unittest
import typing
import datetime as dt

import rocalert.services.sleeptimer as sleeptimer


class MockUserSettings:
    def __init__(
            self,
            usenightmode: bool = False,
            regular_waitrange: typing.Tuple[int, int] = None,
            nightmode_activerange: typing.Tuple[dt.time, dt.time] = None,
            nightmode_waitrange: typing.Tuple[float, float] = None
            ) -> None:
        self.use_nightmode = usenightmode
        self.nightmode_activetime_range = nightmode_activerange
        self.nightmode_waittime_range = nightmode_waitrange
        self.regular_waittimes_seconds = regular_waitrange


class SleepTimerTest(unittest.TestCase):
    def test_when_not_overmidnight_detect_nightmode(self):
        user_settings = MockUserSettings(
            usenightmode=True,
            regular_waitrange=(60, 60),
            nightmode_activerange=(dt.time(0, 0, 0), dt.time(11, 59, 59)),
            nightmode_waitrange=(60, 120))

        timer = sleeptimer.SleepTimer(
            user_settings=user_settings,
            randomlowhigh=lambda x, y: (y-x)/2,
            current_time_getter=lambda: dt.datetime(2022, 12, 25, 6, 0, 0, 0)
            )

        self.assertTrue(timer.in_nightmode())

    def test_when_overmidnight_detect_nightmode(self):
        user_settings = MockUserSettings(
            usenightmode=True,
            regular_waitrange=(60, 60),
            nightmode_activerange=(dt.time(20, 0, 0), dt.time(4, 0, 0)),
            nightmode_waitrange=(60, 120))

        timer = sleeptimer.SleepTimer(
            user_settings=user_settings,
            randomlowhigh=lambda x, y: (y-x)/2,
            current_time_getter=lambda: dt.datetime(2022, 12, 25, 0, 0, 1, 0)
            )

        self.assertTrue(timer.in_nightmode())

    def test_when_notnightmode_not_overmidnight_donot_detect_nightmode_(self):
        user_settings = MockUserSettings(
            usenightmode=True,
            regular_waitrange=(60, 60),
            nightmode_activerange=(dt.time(0, 0, 0), dt.time(11, 59, 59)),
            nightmode_waitrange=(60, 120))

        timer = sleeptimer.SleepTimer(
            user_settings=user_settings,
            randomlowhigh=lambda x, y: (y-x)/2,
            current_time_getter=lambda: dt.datetime(2022, 12, 25, 14, 0, 0, 0)
            )

        self.assertFalse(timer.in_nightmode())

    def test_when_notnightmode_overmidnight_donot_detect_nightmode(self):
        user_settings = MockUserSettings(
            usenightmode=True,
            regular_waitrange=(60, 60),
            nightmode_activerange=(dt.time(20, 0, 0), dt.time(4, 0, 0)),
            nightmode_waitrange=(60, 120))

        timer = sleeptimer.SleepTimer(
            user_settings=user_settings,
            randomlowhigh=lambda x, y: (y-x)/2,
            current_time_getter=lambda: dt.datetime(2022, 12, 25, 15, 0, 1, 0)
            )

        self.assertFalse(timer.in_nightmode())
