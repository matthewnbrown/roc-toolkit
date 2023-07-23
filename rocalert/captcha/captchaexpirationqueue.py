
import asyncio
from rocalert.roc_web_handler import Captcha

from collections import defaultdict
from collections.abc import Awaitable
from enum import Enum, auto
from threading import Lock, Thread, Timer

_eventloop: asyncio.AbstractEventLoop = None


class CaptchaExpirationQueueEvent(Enum):
    CaptchasRemoved = auto()
    CaptchasAdded = auto()
    NoCaptchas = auto()


class CaptchaExpirationQueue:
    def __init__(self) -> None:
        self._captchalock = Lock()
        self._eventlistenerlock = Lock()
        self._captchas: list[Captcha] = []
        self._timer: Timer = None

        self._eventlisteners: dict[CaptchaExpirationQueueEvent,
                                   list[Awaitable]] = defaultdict(list)

    def add(self, captcha: Captcha) -> bool:
        """attempt to add an element to the queue

        Args:
            captcha (Captcha): captcha to be added

        Returns:
            bool: true if added, false otherwise
        """
        if captcha is None or captcha.is_expired:
            return False

        self._captchalock.acquire()
        self._captchas.append(captcha)
        if len(self._captchas) == 1:
            self._refresh_timer()
        self._trigger_events(CaptchaExpirationQueueEvent.CaptchasAdded)
        self._captchalock.release()
        return True

    def pop(self) -> Captcha:
        """pop oldest captcha off queue

        Returns:
            Captcha: oldest captcha, none if there are no captchas
        """
        self._captchalock.acquire()
        oldest_captcha = None

        if any(x for x in self._captchas if not x.is_expired):
            oldest_age = max(x.age for x in self._captchas if not x.is_expired)
            oldest_captcha = next(
                (x for x in self._captchas if x.age == oldest_age), None)
            if oldest_captcha is not None:
                self._captchas.remove(oldest_captcha)
                self._trigger_events(
                    CaptchaExpirationQueueEvent.CaptchasRemoved)
        self._captchalock.release()

        return oldest_captcha

    def remove(self, captcha: Captcha = None, captchahash: str = None) -> bool:
        """attempt to remove element from list

        Args:
            captcha (Captcha, optional): captcha to remove. Defaults to None.
            captchahash (str, optional): hash of captcha to remove. Defaults to None.

        Returns:
            bool: true if removed, false otherwise
        """
        self._captchalock.acquire()
        beforelen = len(self._captchas)
        if captcha is not None:
            self._captchas.remove(captcha)
        else:
            self._captchas = [
                x for x in self._captchas if x.hash != captchahash]
        newlen = len(self._captchas)

        if newlen < beforelen:
            self._trigger_events(CaptchaExpirationQueueEvent.CaptchasRemoved)
        if newlen == 0:
            self._cancel_timer()
            self._trigger_events(CaptchaExpirationQueueEvent.NoCaptchas)

        self._captchalock.release()
        return newlen < beforelen

    def listen(self, event: CaptchaExpirationQueueEvent, method: Awaitable) -> None:
        self._eventlistenerlock.acquire()
        self._eventlisteners[event].append(method)
        self._eventlistenerlock.release()

    def _clear_expired_captchas(self) -> None:
        self._captchalock.acquire()
        anyexpired = any(x.is_expired for x in self._captchas)
        if anyexpired:
            self._captchas = [x for x in self._captchas if not x.is_expired]
            self._trigger_events(CaptchaExpirationQueueEvent.CaptchasRemoved)

        if any(self._captchas):
            self._refresh_timer()
        else:
            self._trigger_events(CaptchaExpirationQueueEvent.NoCaptchas)
            self._cancel_timer()

        self._captchalock.release()

    def _refresh_timer(self) -> None:
        self._cancel_timer()
        self._timer = Timer(5, self._clear_expired_captchas)

    def _cancel_timer(self) -> None:
        if self._timer is not None:
            self._timer.cancel()
            self._timer = None

    def __len__(self):
        self._captchalock.acquire()
        length = len(self._captchas)
        self._captchalock.release()
        return length

    def _trigger_events(self, event: CaptchaExpirationQueueEvent):
        global _eventloop
        self._eventlistenerlock.acquire()
        if _eventloop is None:
            _eventloop = asyncio.new_event_loop()
            Thread(target=_eventloop.run_forever, daemon=True).start()

        for listener in self._eventlisteners[event]:
            _eventloop.call_soon_threadsafe(asyncio.create_task, listener)

        self._eventlistenerlock.release()
