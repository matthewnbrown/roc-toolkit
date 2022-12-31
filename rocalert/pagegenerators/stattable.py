from typing import Tuple
from bs4 import BeautifulSoup

from .generatortools import rocnum_to_int
import rocalert.models.pages.genericpages as gp


class StatTableGenerator:
    @classmethod
    def generate(cls, table: BeautifulSoup) -> gp.StatTable:
        rows = table.find_all('tr')

        strike = cls._parseaction(rows[1])
        defense = cls._parseaction(rows[2])
        spy = cls._parseaction(rows[3])
        sentry = cls._parseaction(rows[4])
        kills = rocnum_to_int(rows[5].contents[3].text)
        killratio = float(rows[6].contents[3].text)

        return gp.StatTable(strike, defense, spy, sentry, kills, killratio)

    @classmethod
    def _parseaction(
            cls, row: BeautifulSoup
            ) -> Tuple[float, rocnum_to_int, int]:

        label = row.contents[1].text
        if '+' in label:
            bonus = float(label[label.index('+')+1: label.index('%')])
        else:
            bonus = 0.0
        action = rocnum_to_int(row.contents[3].text)
        rank = int(row.contents[5].text[1:])

        return gp.StatTableEntry(bonus, action, rank)
