from typing import Union
from datetime import datetime
from bs4 import BeautifulSoup


class RocNumber:
    def __init__(self, value: Union[int, str]) -> None:
        if type(value) == int:
            self._value = value
        elif type(value) == str:
            value = value.strip().split(' ')[0].strip()
            value = value.replace(',', '')
            self._value = int(value)
        else:
            raise ValueError("Value must be a string or integer!")

    @property
    def vajlue(self) -> int:
        return self._value

    def get_prettyvalue(self) -> str:
        return f'{self._value:,}'


class RocPage:
    def __init__(self, page: BeautifulSoup) -> None:
        logform = page.find(id='login_form')
        self._loggedin = logform is None

    @property
    def logged_in(self) -> bool:
        return self._loggedin


class RocUserPage(RocPage):
    def __init__(self, page: BeautifulSoup) -> None:
        super().__init__(page)
        clockbar = page.find(id='clock_bar')
        self._name = clockbar.find(id='topnav_right').text.strip()
        self._rank = clockbar.find(id='s_rank').text
        self._gold = RocNumber(clockbar.find(id='s_gold').text)
        self._turns = RocNumber(clockbar.find(id='s_turns').text)

    @property
    def name(self) -> str:
        return self._name

    @property
    def rank(self) -> str:
        return self._rank

    @property
    def gold(self) -> RocNumber:
        return self._gold

    @property
    def turns(self) -> RocNumber:
        return self._turns

    @property
    def next_turn(self) -> datetime:
        return self._nextturn
