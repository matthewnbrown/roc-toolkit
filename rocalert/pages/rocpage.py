from datetime import datetime
from bs4 import BeautifulSoup


class RocPage:
    def __init__(self, page: BeautifulSoup) -> None:
        pass

    @property
    def logged_in(self):
        return self._loggedin


class RocUserPage(RocPage):
    def __init__(self, page: BeautifulSoup) -> None:
        super().__init__(page)
        pass

    @property
    def name(self) -> str:
        return self._name

    @property
    def rank(self) -> str:
        return self._rank

    @property
    def gold(self) -> int:
        return self._gold

    @property
    def next_turn(self) -> datetime:
        return self._nextturn
