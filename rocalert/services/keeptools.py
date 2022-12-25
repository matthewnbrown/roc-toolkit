import datetime as dt

from rocalert.pages.keep import RocKeepPage
from rocalert.roc_web_handler import RocWebHandler


class KeyRepairError(Exception):
    pass


class KeepKeyRepairer:
    def __init__(self, roc: RocWebHandler) -> None:
        self._roc = roc
        self._repair_finished_time: dt.datetime = None
        self._broken_keys = 0
        self.force_refresh()

    def key_is_repairing(self) -> bool:
        now = dt.datetime.now()
        return self._repair_finished_time > now

    def key_needs_repair(self, keep_page: RocKeepPage = None) -> bool:
        return self._broken_keys > 0 and not self.key_is_repairing()

    def add_broken_keys(self, count) -> None:
        self._broken_keys += count

    def force_refresh(self) -> None:
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
