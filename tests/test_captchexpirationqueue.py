import asyncio
from datetime import datetime, timedelta
import unittest

from mock import patch, AsyncMock, MagicMock
from time import sleep
import rocalert.captcha.captchaexpirationqueue as ceq
from rocalert.captcha.captchaexpirationqueue import CaptchaExpirationQueue, Captcha, CaptchaExpirationQueueEvent


# @patch('threading.Lock')
# @patch('threading.Thread')
# @patch('threading.Timer')
class EventTests(unittest.TestCase):
    def __init__(self, methodName: str = ...) -> None:
        super().__init__(methodName)

    def test_adding_should_trigger_add_event(self):
        sut = CaptchaExpirationQueue()
        captcha = Captcha("abc123", creation_date=datetime.now())

        callsoon_threadsafe = MagicMock()

        ceq._eventloop = asyncio.AbstractEventLoop()
        ceq._eventloop.call_soon_threadsafe = callsoon_threadsafe

        callbackmock = AsyncMock()
        awaitable = callbackmock()
        sut.listen(CaptchaExpirationQueueEvent.CaptchasAdded, awaitable)
        sut.add(captcha)

        callsoon_threadsafe.assert_called_once_with(
            asyncio.create_task, awaitable)

    def test_adding_expiredcatcha_shouldnot_trigger_add_event(self):
        sut = CaptchaExpirationQueue()
        captcha = Captcha(
            "abc123", creation_date=datetime.now()-Captcha.EXPIRATION_AGE-timedelta(days=1))

        callsoon_threadsafe = MagicMock()

        ceq._eventloop = asyncio.AbstractEventLoop()
        ceq._eventloop.call_soon_threadsafe = callsoon_threadsafe

        callbackmock = AsyncMock()
        awaitable = callbackmock()
        sut.listen(CaptchaExpirationQueueEvent.CaptchasAdded, awaitable)
        sut.add(captcha)

        callsoon_threadsafe.assert_not_called()

    def test_adding_should_trigger_add_event(self):
        sut = CaptchaExpirationQueue()
        captcha = Captcha("abc123", creation_date=datetime.now())

        callsoon_threadsafe = MagicMock()

        ceq._eventloop = asyncio.AbstractEventLoop()
        ceq._eventloop.call_soon_threadsafe = callsoon_threadsafe

        callbackmock = AsyncMock()
        awaitable = callbackmock()
        sut.listen(CaptchaExpirationQueueEvent.CaptchasAdded, awaitable)
        sut.add(captcha)

        callsoon_threadsafe.assert_called_once_with(
            asyncio.create_task, awaitable)

    def test_removing_should_trigger_add_event(self):
        sut = CaptchaExpirationQueue()
        captcha = Captcha("abc123", creation_date=datetime.now())

        callsoon_threadsafe = MagicMock()

        ceq._eventloop = asyncio.AbstractEventLoop()
        ceq._eventloop.call_soon_threadsafe = callsoon_threadsafe

        callbackmock = AsyncMock()
        awaitable = callbackmock()
        sut.add(captcha)
        sut.listen(CaptchaExpirationQueueEvent.CaptchasRemoved, awaitable)
        sut.remove(captcha.hash)
        callsoon_threadsafe.assert_called_once_with(
            asyncio.create_task, awaitable)

    def test_removing_nonexistant_captcha_shouldnot_trigger_add_event(self):
        sut = CaptchaExpirationQueue()
        captcha = Captcha("abc123", creation_date=datetime.now())

        callsoon_threadsafe = MagicMock()

        ceq._eventloop = asyncio.AbstractEventLoop()
        ceq._eventloop.call_soon_threadsafe = callsoon_threadsafe

        callbackmock = AsyncMock()
        awaitable = callbackmock()
        sut.add(captcha)
        sut.listen(CaptchaExpirationQueueEvent.CaptchasRemoved, awaitable)
        sut.remove("dasfdsff")
        callsoon_threadsafe.assert_not_called()

    def test_removing_allcaptchas_should_trigger_nocaptcha_event(self):
        sut = CaptchaExpirationQueue()
        captcha = Captcha("abc123", creation_date=datetime.now())

        callsoon_threadsafe = MagicMock()

        ceq._eventloop = asyncio.AbstractEventLoop()
        ceq._eventloop.call_soon_threadsafe = callsoon_threadsafe

        callbackmock = AsyncMock()
        awaitable = callbackmock()
        sut.add(captcha)
        sut.listen(CaptchaExpirationQueueEvent.NoCaptchas, awaitable)
        sut.remove(captcha.hash)

        callsoon_threadsafe.assert_called_once_with(
            asyncio.create_task, awaitable)


class QueueTests(unittest.TestCase):
    def __init__(self, methodName: str = ...) -> None:
        super().__init__(methodName)

    def test_pop_should_return_none_when_nocaptchas(self):
        sut = CaptchaExpirationQueue()
        captcha = Captcha("abc123", creation_date=datetime.now())

        sut.add(captcha)
        sut.remove(captcha=captcha)

        result = sut.pop()
        self.assertIsNone(result)

    def test_adding_captchas_increases_length(self):
        sut = CaptchaExpirationQueue()
        captcha = Captcha("abc123", creation_date=datetime.now())
        captcha2 = Captcha("abc124", creation_date=datetime.now())
        captcha3 = Captcha("abc125", creation_date=datetime.now())

        self.assertEqual(len(sut), 0)
        sut.add(captcha)
        self.assertEqual(len(sut), 1)
        sut.add(captcha2)
        sut.add(captcha3)
        self.assertEqual(len(sut), 3)

    def test_removing_captchas_decreases_length(self):
        sut = CaptchaExpirationQueue()
        captcha = Captcha("abc123", creation_date=datetime.now())
        captcha2 = Captcha("abc124", creation_date=datetime.now())
        captcha3 = Captcha("abc125", creation_date=datetime.now())

        self.assertEqual(len(sut), 0)
        sut.add(captcha)
        sut.add(captcha2)
        sut.add(captcha3)
        sut.remove(captcha)
        self.assertEqual(len(sut), 2)
        sut.remove(captcha2)
        sut.remove(captcha3)
        self.assertEqual(len(sut), 0)

    def test_removing_captchahash_decreases_length(self):
        sut = CaptchaExpirationQueue()
        captcha = Captcha("abc123", creation_date=datetime.now())
        captcha2 = Captcha("abc124", creation_date=datetime.now())
        captcha3 = Captcha("abc125", creation_date=datetime.now())

        self.assertEqual(len(sut), 0)
        sut.add(captcha)
        sut.add(captcha2)
        sut.add(captcha3)
        sut.remove(captchahash=captcha.hash)
        self.assertEqual(len(sut), 2)
        sut.remove(captchahash=captcha2.hash)
        sut.remove(captchahash=captcha3.hash)
        self.assertEqual(len(sut), 0)

    def test_removing_captcha_priority_over_hash(self):
        sut = CaptchaExpirationQueue()
        captcha = Captcha("abc123", creation_date=datetime.now())
        captcha2 = Captcha("abc124", creation_date=datetime.now())

        sut.add(captcha)
        sut.add(captcha2)
        self.assertEqual(len(sut), 2)
        sut.remove(captcha=captcha, captchahash=captcha2.hash)
        self.assertEqual(len(sut), 1)

        result = sut.pop()

        self.assertEqual(result, captcha2)

    def test_pop_returns_oldest_captcha(self):
        sut = CaptchaExpirationQueue()
        oldestcaptcha = Captcha("abc123", creation_date=datetime.now(
        )-(Captcha.EXPIRATION_AGE-timedelta(seconds=5)))
        captcha2 = Captcha("abc124", creation_date=datetime.now(
        )-(Captcha.EXPIRATION_AGE-timedelta(seconds=55)))
        captcha3 = Captcha("abc125", creation_date=datetime.now())

        sut.add(captcha2)
        sut.add(oldestcaptcha)
        sut.add(captcha3)

        result = sut.pop()

        self.assertEqual(result, oldestcaptcha)

    def test_pop_does_not_return_expired_captcha(self):
        sut = CaptchaExpirationQueue()
        Captcha.EXPIRATION_AGE = timedelta(hours=1)
        expiredcaptcha = Captcha("abc123", creation_date=datetime.now(
        )-timedelta(minutes=5))

        sut.add(expiredcaptcha)
        Captcha.EXPIRATION_AGE = timedelta(minutes=1)

        self.assertTrue(expiredcaptcha.is_expired)

        result = sut.pop()

        self.assertIsNone(result)


class TimerTests(unittest.TestCase):
    def test_starts_with_no_timer(self):
        sut = CaptchaExpirationQueue()
        self.assertIsNone(sut._timer)
