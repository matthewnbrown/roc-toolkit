from bs4 import BeautifulSoup

import rocalert.models.pages.genericpages as gp
import rocalert.models.pages.training as roctraining


class TrainingDetailsGenerator:
    @classmethod
    def generate(cls, soup: BeautifulSoup) -> roctraining.TrainingDetails:
        content = soup.find(id='content')
        trainingdetails = roctraining.TrainingDetails()
        fpc = content.find_all('div', {'class': 'flexpanel_container'})
        cls._get_allsoldier_cost(fpc[0], trainingdetails)
        cls._get_mercs_avail(fpc[0], trainingdetails)

        fpctables = fpc[1].find_all('table')
        cls._get_troops_table(fpctables[1], trainingdetails)

        return trainingdetails

    @classmethod
    def _get_soldiersoldier_cost(
            cls, content: BeautifulSoup, id: str) -> int:
        eles = content.find(id=id).find_all('span', {'class': 'cost'})

        cost = eles[0].text.split(' ')[0]
        return gp.rocnum_to_int(cost)

    @classmethod
    def _get_allsoldier_cost(
            cls,
            content: BeautifulSoup,
            details: roctraining.TrainingDetails
            ) -> None:
        details.attack_sold_cost = cls._get_soldiersoldier_cost(
            content, 'cell_train_attack_soldiers')
        details.defense_sold_cost = cls._get_soldiersoldier_cost(
            content, 'cell_train_defense_soldiers')
        details.spy_sold_cost = cls._get_soldiersoldier_cost(
            content, 'cell_train_spies')
        details.sentry_sold_cost = cls._get_soldiersoldier_cost(
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
            cls,
            content: BeautifulSoup,
            details: roctraining.TrainingDetails) -> None:
        details.avail_attack_mercs = cls._merc_entry_creator(
            content, 'cell_merc_attack_mercs')
        details.avail_defense_mercs = cls._merc_entry_creator(
            content, 'cell_merc_defense_mercs')
        details.avail_untrained_mercs = cls._merc_entry_creator(
            content, 'cell_merc_untrained_mercs')

    @classmethod
    def _parse_soldierrow(
            cls, row: BeautifulSoup
            ) -> roctraining.RocTrainingTableEntry:
        return roctraining.RocTrainingTableEntry(
                gp.rocnum_to_int(row.contents[3].text),
                gp.rocnum_to_int(row.contents[5].text))

    @classmethod
    def _get_troops_table(
            cls,
            table: BeautifulSoup,
            details: roctraining.TrainingDetails
            ) -> None:
        rows = table.find_all('tr')
        details.attack_soldiers = cls._parse_soldierrow(rows[2])
        details.attack_mercenaries = cls._parse_soldierrow(rows[3])
        details.defense_soldiers = cls._parse_soldierrow(rows[4])
        details.defense_mercenaries = cls._parse_soldierrow(rows[5])
        details.untrained_soldiers = cls._parse_soldierrow(rows[6])
        details.untrained_mercenaries = cls._parse_soldierrow(rows[7])
        details.spies = cls._parse_soldierrow(rows[8])
        details.sentries = cls._parse_soldierrow(rows[9])
        details.zombies = cls._parse_soldierrow(rows[10])
        details.total_mercenaries = cls._parse_soldierrow(rows[11])
        details.total_soldiers = cls._parse_soldierrow(rows[12])
        details.total_covert_force = cls._parse_soldierrow(rows[13])
        details.total_fighting_force = cls._parse_soldierrow(rows[14])
