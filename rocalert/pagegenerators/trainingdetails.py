from bs4 import BeautifulSoup

from .generatortools import dataclass_from_dict
import rocalert.models.pages.genericpages as gp
import rocalert.models.pages.training as roctraining


class TrainingDetailsGenerator:
    @classmethod
    def generate(cls, soup: BeautifulSoup) -> roctraining.TrainingDetails:
        content = soup.find(id='content')
        detailmap = {}
        fpc = content.find_all('div', {'class': 'flexpanel_container'})
        cls._get_allsoldier_cost(fpc[0], detailmap)
        cls._get_mercs_avail(fpc[0], detailmap)

        fpctables = fpc[1].find_all('table')
        cls._get_troops_table(fpctables[1], detailmap)

        return dataclass_from_dict(
            roctraining.TrainingDetails, detailmap)

    @classmethod
    def _get_soldiersoldier_cost(
            cls, content: BeautifulSoup, id: str) -> int:
        eles = content.find(id=id).find_all('span', {'class': 'cost'})

        cost = eles[0].text.split(' ')[0]
        return gp.rocnum_to_int(cost)

    @classmethod
    def _get_allsoldier_cost(
            cls, content: BeautifulSoup, detailmap: dict
            ) -> None:
        detailmap['attack_sold_cost'] = cls._get_soldiersoldier_cost(
            content, 'cell_train_attack_soldiers')
        detailmap['defense_sold_cost'] = cls._get_soldiersoldier_cost(
            content, 'cell_train_defense_soldiers')
        detailmap['spy_sold_cost'] = cls._get_soldiersoldier_cost(
            content, 'cell_train_spies')
        detailmap['sentry_sold_cost'] = cls._get_soldiersoldier_cost(
            content, 'cell_train_sentries')

    @classmethod
    def _merc_entry_creator(
            cls, content: BeautifulSoup, id: str
            ) -> roctraining.RocTrainingTableEntry:
        merc_span = content.find(id=id).find_all('span')
        if 'None' in merc_span[0].text:
            count_str = '0'
        else:
            count_str = merc_span[0].text.split(' ')[1]

        merc_entry = roctraining.RocTrainingTableEntry(
            gp.rocnum_to_int(count_str),
            gp.rocnum_to_int(merc_span[1].text.replace('Gold', '')))

        return merc_entry

    @classmethod
    def _get_mercs_avail(
            cls, content: BeautifulSoup, detailmap: dict) -> None:
        detailmap['avail_attack_mercs'] = cls._merc_entry_creator(
            content, 'cell_merc_attack_mercs')
        detailmap['avail_defense_mercs'] = cls._merc_entry_creator(
            content, 'cell_merc_defense_mercs')
        detailmap['avail_untrained_mercs'] = cls._merc_entry_creator(
            content, 'cell_merc_untrained_mercs')

    @classmethod
    def _parse_row(
            cls, row: BeautifulSoup
            ) -> roctraining.RocTrainingTableEntry:
        return roctraining.RocTrainingTableEntry(
                gp.rocnum_to_int(row.contents[3].text),
                gp.rocnum_to_int(row.contents[5].text))

    @classmethod
    def _get_troops_table(
            cls, table: BeautifulSoup, detailmap: dict
            ) -> None:
        rows = table.find_all('tr')
        detailmap['attack_soldiers'] = cls._parse_row(rows[2])
        detailmap['attack_mercenaries'] = cls._parse_row(rows[3])
        detailmap['defense_soldiers'] = cls._parse_row(rows[4])
        detailmap['defense_mercenaries'] = cls._parse_row(rows[5])
        detailmap['untrained_soldiers'] = cls._parse_row(rows[6])
        detailmap['untrained_mercenaries'] = cls._parse_row(rows[7])
        detailmap['spies'] = cls._parse_row(rows[8])
        detailmap['sentries'] = cls._parse_row(rows[9])
        detailmap['zombies'] = cls._parse_row(rows[10])
        detailmap['total_mercenaries'] = cls._parse_row(rows[11])
        detailmap['total_soldiers'] = cls._parse_row(rows[12])
        detailmap['total_covert_force'] = cls._parse_row(rows[13])
        detailmap['total_fighting_force'] = cls._parse_row(rows[14])
