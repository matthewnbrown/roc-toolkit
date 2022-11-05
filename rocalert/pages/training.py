from dataclasses import dataclass
import rocalert.pages.genericpages as genpages
from bs4 import BeautifulSoup


@dataclass
class RocTrainingTableEntry:
    count: int
    income: int


class RocTrainingPage(genpages.RocImageCaptchaPage):
    def __init__(self, page: BeautifulSoup) -> None:
        super().__init__(page)

        content = page.find(id='content')
        fpc = content.find_all('div', {'class': 'flexpanel_container'})
        self._get_mercs_avail(fpc[0])

        fpctables = fpc[1].find_all('table')
        self._stattable = genpages.StatTable(fpctables[0])
        self._weapondisttable = genpages.WeaponTroopDistTable(fpctables[2])

        self._get_troops_table(fpctables[1])

    def _merc_entry_creator(
            self, content: BeautifulSoup, id: str) -> RocTrainingTableEntry:
        merc_span = content.find(id=id).find_all('span')
        if 'None' in merc_span[0].text:
            count_str = '0'
        else:
            count_str = merc_span[0].text.split(' ')[1]

        merc_entry = RocTrainingTableEntry(
            genpages.rocnum_to_int(count_str),
            genpages.rocnum_to_int(merc_span[1].text.replace('Gold', '')))

        return merc_entry

    def _get_mercs_avail(self, content: BeautifulSoup) -> None:
        self._availattmercs = self._merc_entry_creator(
            content, 'cell_merc_attack_mercs')
        self._availdefmercs = self._merc_entry_creator(
            content, 'cell_merc_defense_mercs')
        self._availuntmercs = self._merc_entry_creator(
            content, 'cell_merc_untrained_mercs')

    def _parse_row(self, row: BeautifulSoup) -> RocTrainingTableEntry:
        return RocTrainingTableEntry(
                genpages.rocnum_to_int(row.contents[3].text),
                genpages.rocnum_to_int(row.contents[5].text))

    def _get_troops_table(self, table: BeautifulSoup) -> None:
        rows = table.find_all('tr')
        self._attacksold = self._parse_row(rows[2])
        self._attackmercs = self._parse_row(rows[3])
        self._defensesold = self._parse_row(rows[4])
        self._defensemercs = self._parse_row(rows[5])
        self._untrainedsold = self._parse_row(rows[6])
        self._untrainedmercs = self._parse_row(rows[7])
        self._spies = self._parse_row(rows[8])
        self._sentries = self._parse_row(rows[9])
        self._zombies = self._parse_row(rows[10])
        self._totalmercs = self._parse_row(rows[11])
        self._totalsoldiers = self._parse_row(rows[12])
        self._totalcovert = self._parse_row(rows[13])
        self._tff = self._parse_row(rows[14])

    @property
    def weapon_distribution_table(self) -> genpages.WeaponTroopDistTable:
        return self._weapondisttable

    @property
    def stats_table(self) -> genpages.StatTable:
        return self._stattable

    @property
    def attack_soldiers(self) -> RocTrainingTableEntry:
        return self._attacksold

    @property
    def attack_mercenaries(self) -> RocTrainingTableEntry:
        return self._attackmercs

    @property
    def defense_soldiers(self) -> RocTrainingTableEntry:
        return self._defensesold

    @property
    def defense_mercenaries(self) -> RocTrainingTableEntry:
        return self._defensemercs

    @property
    def untrained_soldiers(self) -> RocTrainingTableEntry:
        return self._untrainedsold

    @property
    def untrained_mercenaries(self) -> RocTrainingTableEntry:
        return self._untrainedmercs

    @property
    def spies(self) -> RocTrainingTableEntry:
        return self._spies

    @property
    def sentries(self) -> RocTrainingTableEntry:
        return self._sentries

    @property
    def zombies(self) -> RocTrainingTableEntry:
        return self._zombies

    @property
    def total_soldiers(self) -> RocTrainingTableEntry:
        return self._totalsoldiers

    @property
    def total_mercenaries(self) -> RocTrainingTableEntry:
        return self._totalmercs

    @property
    def total_covert_force(self) -> RocTrainingTableEntry:
        return self._totalcovert

    @property
    def total_fighting_force(self) -> RocTrainingTableEntry:
        return self._tff

    @property
    def avail_attack_mercs(self) -> RocTrainingTableEntry:
        return self._availattmercs

    @property
    def avail_defense_mercs(self) -> RocTrainingTableEntry:
        return self._availdefmercs

    @property
    def avail_untrained_mercs(self) -> RocTrainingTableEntry:
        return self._availuntmercs
