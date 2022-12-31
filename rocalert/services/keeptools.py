import datetime as dt

from rocalert.models.pages.keep import KeepPage
from rocalert.roc_web_handler import RocWebHandler


class KeyRepairError(Exception):
    pass


class KeepKeyRepairerABC():
    def key_is_repairing(self) -> bool:
        raise NotImplementedError()

    def key_needs_repair(self, keep_page: KeepPage = None) -> bool:
        raise NotImplementedError()

    def add_broken_keys(self, count) -> None:
        raise NotImplementedError()

    def update_keep_status(self) -> None:
        raise NotImplementedError()

    def repair_key(self) -> None:
        raise NotImplementedError()


class KeepKeyRepairer(KeepKeyRepairerABC):
    def __init__(self, roc: RocWebHandler) -> None:
        self._roc = roc
        self._repair_finished_time: dt.datetime = None
        self._broken_keys = None

    def _initalization_check(self):
        if self._broken_keys is None or self._repair_finished_time is None:
            msg = 'Key repairer status must be updated before using.'
            raise KeyRepairError(msg)

    def key_is_repairing(self) -> bool:
        self._initalization_check()
        now = dt.datetime.now()
        return self._repair_finished_time > now

    def key_needs_repair(self, keep_page: KeepPage = None) -> bool:
        self._initalization_check()
        return self._broken_keys > 0 and not self.key_is_repairing()

    def add_broken_keys(self, count) -> None:
        self._initalization_check()
        self._broken_keys += count

    def update_keep_status(self) -> None:
        keeppage = self._roc.get_keep_page()

        self._broken_keys = keeppage.broken_key_count
        if keeppage.repairing:
            self._repair_finished_time = keeppage.finish_repair_time
        else:
            self._repair_finished_time = dt.datetime.now()

    def repair_key(self) -> None:
        keeppage = self._roc.get_keep_page()

        if keeppage.repairing:
            msg = 'Cannot repair key is one is already being repaired!'
            raise KeyRepairError(msg)
        if keeppage.broken_key_count <= 0:
            msg = f'Cannot repair key! Keycount is {keeppage.broken_key_count}'
            raise KeyRepairError(msg)

        self._roc.start_key_repair()
