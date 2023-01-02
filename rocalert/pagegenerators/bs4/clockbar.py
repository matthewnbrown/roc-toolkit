from bs4 import BeautifulSoup
import datetime as dt

from rocalert.logging import DateTimeGeneratorABC
import rocalert.models.pages.genericpages as gp
from .generatortools import rocnum_to_int


class ClockBarGenerator:
    @classmethod
    def generate(
            cls,
            pagesoup: BeautifulSoup,
            timegenerator: DateTimeGeneratorABC) -> gp.ClockBar:
        clockbar = pagesoup.find(id='clock_bar')
        time_till_nextturn = cls._get_timedelta_to_nextturn(
            (clockbar.find(id='s_next').text)
        )
        return gp.ClockBar(
            name=pagesoup.find(id='topnav_right').text.strip(),
            rank=int(clockbar.find(id='s_rank').text),
            gold=rocnum_to_int(clockbar.find(id='s_gold').text),
            turns=rocnum_to_int(clockbar.find(id='s_turns').text),
            next_turn=timegenerator.get_current_time() + time_till_nextturn
        )

    @classmethod
    def _get_timedelta_to_nextturn(cls, nextturntext: str) -> dt.timedelta:
        minutes, seconds = nextturntext.split(':')
        return dt.timedelta(minutes=int(minutes), seconds=int(seconds))
