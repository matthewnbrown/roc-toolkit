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
    def test_when_not_overmidnight_should_detect_nightmode(self):
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

    def test_when_overmidnight_should_detect_nightmode(self):
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

    def test_when_nightmode_disabled_and_within_nightmode_hours_not_innightmode(self):  # noqa: 501
        user_settings = MockUserSettings(
            usenightmode=False,
            regular_waitrange=(60, 60),
            nightmode_activerange=(dt.time(0, 0, 0), dt.time(12, 0, 0)),
            nightmode_waitrange=(60, 120))

        timer = sleeptimer.SleepTimer(
            user_settings=user_settings,
            randomlowhigh=lambda x, y: (y-x)/2,
            current_time_getter=lambda: dt.datetime
            (year=2022, month=12, day=25, hour=6, minute=0, second=1)
            )

        self.assertFalse(timer.in_nightmode())

    def test_when_nightmode_disabled_and_notwithin_nightmode_hours_not_innightmode(self):  # noqa: 501
        user_settings = MockUserSettings(
            usenightmode=False,
            regular_waitrange=(60, 60),
            nightmode_activerange=(dt.time(0, 0, 0), dt.time(12, 0, 0)),
            nightmode_waitrange=(60, 120))

        timer = sleeptimer.SleepTimer(
            user_settings=user_settings,
            randomlowhigh=lambda x, y: (y-x)/2,
            current_time_getter=lambda: dt.datetime
            (year=2022, month=12, day=25, hour=13, minute=0, second=1)
            )

        self.assertFalse(timer.in_nightmode())

    def test_when_nightmode_lowrange_withinbounds(self):  # noqa: 501
        lowerbound, highbound = 60, 120
        user_settings = MockUserSettings(
            usenightmode=True,
            regular_waitrange=(60, 60),
            nightmode_activerange=(dt.time(0, 0, 0), dt.time(12, 0, 0)),
            nightmode_waitrange=(lowerbound, highbound))

        timer = sleeptimer.SleepTimer(
            user_settings=user_settings,
            randomlowhigh=lambda x, y: x,
            current_time_getter=lambda: dt.datetime
            (year=2022, month=12, day=25, hour=6, minute=0, second=1)
            )

        wait_time = timer.calculate_sleeptime()

        self.assertGreaterEqual(wait_time, lowerbound*60)
        self.assertLessEqual(wait_time, highbound*60)

    def test_when_nightmode_highrange_withinbounds(self):  # noqa: 501
        lowerbound, highbound = 60, 120
        user_settings = MockUserSettings(
            usenightmode=True,
            regular_waitrange=(60, 60),
            nightmode_activerange=(dt.time(0, 0, 0), dt.time(12, 0, 0)),
            nightmode_waitrange=(lowerbound, highbound))

        timer = sleeptimer.SleepTimer(
            user_settings=user_settings,
            randomlowhigh=lambda x, y: y,
            current_time_getter=lambda: dt.datetime
            (year=2022, month=12, day=25, hour=6, minute=0, second=1)
            )

        wait_time = timer.calculate_sleeptime()

        self.assertGreaterEqual(wait_time, lowerbound*60)
        self.assertLessEqual(wait_time, highbound*60)

    def test_when_nightmode_midrange_withinbounds(self):  # noqa: 501
        lowerbound, highbound = 60, 120
        user_settings = MockUserSettings(
            usenightmode=True,
            regular_waitrange=(60, 60),
            nightmode_activerange=(dt.time(0, 0, 0), dt.time(12, 0, 0)),
            nightmode_waitrange=(lowerbound, highbound))

        timer = sleeptimer.SleepTimer(
            user_settings=user_settings,
            randomlowhigh=lambda x, y: (y-x)/2,
            current_time_getter=lambda: dt.datetime
            (year=2022, month=12, day=25, hour=6, minute=0, second=1)
            )

        wait_time = timer.calculate_sleeptime()

        self.assertGreaterEqual(wait_time, lowerbound*60)
        self.assertLessEqual(wait_time, highbound*60)

    def test_when_nightmode_should_not_sleep_morethan_given_value_past_nightmode_end(self):  # noqa: 501
        max_mins_past_nightmode = 15
        user_settings = MockUserSettings(
            usenightmode=True,
            regular_waitrange=(60, 60),
            nightmode_activerange=(dt.time(0, 0, 0), dt.time(6, 0, 0)),
            nightmode_waitrange=(60, 120))

        curtime = dt.datetime(
            year=2022, month=12, day=25, hour=5, minute=50, second=0)

        timer = sleeptimer.SleepTimer(
            user_settings=user_settings,
            randomlowhigh=lambda x, y: y,
            current_time_getter=lambda: curtime,
            max_postnightmode_sleeptime_mins=max_mins_past_nightmode
            )

        sleeplength = timer.calculate_sleeptime()

        self.assertGreaterEqual(sleeplength, 600)
        self.assertLessEqual(sleeplength, 25*60)

    def test_when_regularmode_midrange_withinbounds(self):  # noqa: 501
        lowend, highend = 300, 600
        user_settings = MockUserSettings(
            usenightmode=False,
            regular_waitrange=(lowend, highend))

        curtime = dt.datetime(
            year=2022, month=12, day=25, hour=5, minute=50, second=0)

        timer = sleeptimer.SleepTimer(
            user_settings=user_settings,
            randomlowhigh=lambda x, y: (y-x)/2,
            current_time_getter=lambda: curtime
            )

        sleeplength = timer.calculate_sleeptime()

        self.assertGreaterEqual(sleeplength, lowend)
        self.assertLessEqual(sleeplength, highend)

    def test_when_regularmode_lowend_withinbounds(self):  # noqa: 501
        lowend, highend = 300, 600
        user_settings = MockUserSettings(
            usenightmode=False,
            regular_waitrange=(lowend, highend))

        curtime = dt.datetime(
            year=2022, month=12, day=25, hour=5, minute=50, second=0)

        timer = sleeptimer.SleepTimer(
            user_settings=user_settings,
            randomlowhigh=lambda x, y: x,
            current_time_getter=lambda: curtime
            )

        sleeplength = timer.calculate_sleeptime()

        self.assertGreaterEqual(sleeplength, lowend)
        self.assertLessEqual(sleeplength, highend)

    def test_when_regularmode_highend_withinbounds(self):  # noqa: 501
        lowend, highend = 300, 600
        user_settings = MockUserSettings(
            usenightmode=False,
            regular_waitrange=(lowend, highend))

        curtime = dt.datetime(
            year=2022, month=12, day=25, hour=5, minute=50, second=0)

        timer = sleeptimer.SleepTimer(
            user_settings=user_settings,
            randomlowhigh=lambda x, y: y,
            current_time_getter=lambda: curtime
            )

        sleeplength = timer.calculate_sleeptime()

        self.assertGreaterEqual(sleeplength, lowend)
        self.assertLessEqual(sleeplength, highend)
