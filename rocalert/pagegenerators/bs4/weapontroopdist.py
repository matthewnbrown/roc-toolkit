from bs4 import BeautifulSoup


from .generatortools import rocnum_to_int
import rocalert.models.pages.genericpages as gp


class WeaponTroopDistTableGenerator:
    @classmethod
    def generate(cls, table: BeautifulSoup) -> gp.WeaponTroopDistTable:
        tbody = table.find('tbody')
        table = tbody if tbody else table

        rows = table.find_all('tr')

        att_wtdist = gp.WeaponDistTableEntry(
            rocnum_to_int(rows[2].contents[5].text.split(' ')[0]),
            rocnum_to_int(rows[2].contents[3].text))

        def_wtdist = gp.WeaponDistTableEntry(
            rocnum_to_int(rows[3].contents[5].text.split(' ')[0]),
            rocnum_to_int(rows[3].contents[3].text))

        spy_wtdist = gp.WeaponDistTableEntry(
            rocnum_to_int(rows[4].contents[5].text),
            rocnum_to_int(rows[4].contents[3].text))

        sentry_wtdist = gp.WeaponDistTableEntry(
            rocnum_to_int(rows[5].contents[5].text),
            rocnum_to_int(rows[5].contents[3].text))

        tffeles = rows[6].find_all('td')
        tff = gp.WeaponDistTableEntry(rocnum_to_int(tffeles[2].text))
        tcfeles = rows[7].find_all('td')
        tcf = gp.WeaponDistTableEntry(rocnum_to_int(tcfeles[2].text))
        untrained = gp.WeaponDistTableEntry(
            cls._extract_untrained(rows[2].contents[5].text))

        return gp.WeaponTroopDistTable(
            att_wtdist, def_wtdist, spy_wtdist, sentry_wtdist,
            tcf, untrained, tff
        )

    @classmethod
    def _extract_untrained(cls, attacksoldiers: str) -> int:
        split = attacksoldiers.split(' ')
        if len(split) != 3:
            return 0
        num = split[1]
        return rocnum_to_int(num.split('+', maxsplit=1)[1])
