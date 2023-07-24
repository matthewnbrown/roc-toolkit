from rocalert.captcha.captchaexpirationqueue import CaptchaExpirationQueue, CaptchaExpirationQueueEvent
from rocalert.roc_web_handler import Captcha

from threading import Lock
from typing import Callable


class CaptchaCacheManager:
    def __init__(self, captchaprovider: Callable[[], Captcha], cachesize: int = 5) -> None:
        self._cachesize = cachesize
        self._cachelock = Lock()
        self._cache = CaptchaExpirationQueue()
        self._captchaprovider = captchaprovider
        self._captcharemovedlistener = None

    def clear(self) -> None:
        self._cachelock.acquire()
        while self._cache.pop() is not None:
            continue
        self._cachelock.release()

    def get_latest(self) -> Captcha:
        captcha = None
        while captcha is None:
            self._cachelock.acquire()
            captcha = self._cache.pop()
            self._cachelock.release()
        return captcha

    def __len__(self) -> int:
        self._cachelock.acquire()
        length = len(self._cache)
        self._cachelock.release()
        return length

    def _on_captcha_removed(self) -> None:
        self._cachelock.acquire()

        while len(self._cache) < self._cachesize:
            captcha = self._captchaprovider()
            self._cache.add(captcha)

        self._cachelock.release()

    def start(self) -> None:
        async def on_captcharemoved():
            self._on_captcha_removed()

        self._captcharemovedlistener = on_captcharemoved
        self._cache.listen(
            CaptchaExpirationQueueEvent.CaptchasRemoved, on_captcharemoved)

        self._on_captcha_removed()
