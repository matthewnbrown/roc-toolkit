from bs4 import BeautifulSoup

import rocalert.models.pages.genericpages as gp
from .generatortools import rocnum_to_int, timestamp_to_datetime


class ClockBarGenerator:
    @classmethod
    def generate(cls, pagesoup: BeautifulSoup) -> gp.ClockBar:
        clockbar = pagesoup.find(id='clock_bar')
        return gp.ClockBar(
            name=pagesoup.find(id='topnav_right').text.strip(),
            rank=int(clockbar.find(id='s_rank').text),
            gold=rocnum_to_int(clockbar.find(id='s_gold').text),
            turns=rocnum_to_int(clockbar.find(id='s_turns').text),
            next_turn=timestamp_to_datetime(clockbar.find(id='s_next').text)
        )
