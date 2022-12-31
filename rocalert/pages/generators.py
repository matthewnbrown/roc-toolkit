import abc
import datetime as dt
import dataclasses
from typing import Tuple
from bs4 import BeautifulSoup

import rocalert.models as rocmodels
import rocalert.pages.genericpages as gp
import rocalert.pages.keep as rockeep
import rocalert.pages.armory as rocarmory
import rocalert.pages.base as rocbase
import rocalert.pages.recruit as rocrecruit
import rocalert.pages.training as roctraining


def dataclass_from_dict(klass, d):
    try:
        fieldtypes = {f.name: f.type for f in dataclasses.fields(klass)}
        return klass(**{f: dataclass_from_dict(fieldtypes[f], d[f]) for f in d})
    except: # noqa E722
        return d  # Not a dataclass field


def _timestamp_to_datetime(timestamp: int) -> dt.datetime:
    return dt.datetime.fromtimestamp(timestamp)


def rocnum_to_int(num_as_str: str):
    value = num_as_str.strip().split(' ')[0].strip()
    value = value.replace(',', '')
    return int(value)


def int_to_rocnum(num: int):
    return f'{num:,}'


class PageGenerationException(Exception):
    pass


class ROCPageGeneratorABC(abc.ABC):
    @abc.abstractmethod
    def generate(self, pagehtml: str) -> gp.RocPage:
        msg = f'{self.__class__.__name__} is an ABC'
        raise NotImplementedError(msg)


class BeautifulSoupPageGenerator(ROCPageGeneratorABC):
    def __init__(self, parser=None) -> None:
        self._parser = parser

    def generate(self, pagehtml: str) -> gp.RocPage:
        creation_date = dt.datetime.now()
        soup = BeautifulSoup(pagehtml, self._parser)

        logged_in = self._is_loggedin(soup)

    @staticmethod
    def _is_loggedin(soup: BeautifulSoup) -> bool:
        return soup.find(id='login_form') is None

    @staticmethod
    def _parse_captcha_hash(soup: BeautifulSoup) -> str:
        captchasoup = soup.find(id='captcha_image')

        if captchasoup is None:
            return None
        else:
            return captchasoup.get('src').split('=')[1]


class RocPageGenerator:
    @classmethod
    def generate(cls, soup: BeautifulSoup) -> gp.RocPage:
        pass


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


class KeepStatusGenerator:
    @classmethod
    def generate(cls, soup: BeautifulSoup) -> rockeep.KeepDetails:
        content = soup.find(id='content')
        keystatusarea = content.contents[5]
        keyspan = keystatusarea.find('span')

        keycounts = keyspan.find_all('b')
        keytypes = keyspan.find_all('small')

        keycount = 0
        brokenkeycount = 0

        for i in range(len(keycounts)):
            count = int(keycounts[i].text)
            keytype = keytypes[i].text

            if 'broken' in keytype:
                brokenkeycount += count
            else:
                keycount += count

        cd = content.find('span', {'class': 'countdown'})
        if cd:
            fintimestr = int(cd.get('data-timestamp'))
            repfinishtime = _timestamp_to_datetime(fintimestr)
        else:
            repfinishtime = None

        return rockeep.KeepDetails(
            repairing=repfinishtime is not None,
            finish_repair_time=repfinishtime,
            key_count=keycount,
            broken_key_count=brokenkeycount
        )


class ArmoryDetailsGenerator:
    @classmethod
    def generate(cls, soup: BeautifulSoup) -> rocmodels.ArmoryModel:
        content = soup.find(id='content')
        armory = content.find(id='armory')
        weaponmap = cls._parseweapons_map(armory)

        armorymodel = dataclass_from_dict(rocmodels.ArmoryModel, weaponmap)
        return armorymodel

    @classmethod
    def _parseweapons_map(cls, armory: BeautifulSoup) -> None:
        weapons = {}

        weaponmap = {
            1: 'dagger',
            2: 'maul',
            3: 'blade',
            4: 'excalibur',
            5: 'sai',
            6: 'shield',
            7: 'mithril',
            8: 'dragonskin',
            9: 'cloak',
            10: 'hook',
            11: 'pickaxe',
            12: 'horn',
            13: 'guard_dog',
            14: 'torch'
        }
        for i in range(1, len(weaponmap)+1):
            weapon = armory.find(id=f'weapon{i}')
            count = weapon.find('span', {'class': 'amount'}).text
            cost = weapon.find('span', {'class': 'cost'}).text
            weapons[weaponmap[i]] = rocmodels.ItemCostPair(
                count=gp.rocnum_to_int(count),
                cost=gp.rocnum_to_int(cost))

        return weapons


# TODO: FINISH IMPLEMENTING THIS
class BaseDetailsGenerator:
    @classmethod
    def generate(cls, soup: BeautifulSoup) -> rocbase.BaseDetails:
        base_container = soup.find(id='base_container')

        basedetails = {}
        cls._get_base_details(base_container, basedetails)
        cls._get_events(base_container, basedetails)
        cls._get_recent_activity(base_container, basedetails)
        cls._get_soldier_source_table(base_container, basedetails)
        cls._get_personal_totals_table(base_container, basedetails)
        return dataclass_from_dict(rocbase.BaseDetails, basedetails)

    @classmethod
    def _get_base_details(
            cls,
            base_container: BeautifulSoup,
            basedetails: dict) -> None:
        pass

    @classmethod
    def _get_events(
            cls, base_container: BeautifulSoup
            ) -> list[rocbase.RocEvent]:
        eventlist = base_container.find(id='events')
        listitems = eventlist.findChildren(
            'li', {'class', 'td'}, recursive=False)
        events = []

        def is_event(eventsoup: BeautifulSoup) -> bool:
            isevent = eventsoup.find('span', {'class': 'countdown'})
            return isevent is not None

        def is_current(eventsoup: BeautifulSoup) -> bool:
            return 'ends in' in eventsoup.text

        def get_name(eventsoup: BeautifulSoup) -> str:
            return eventsoup.find('b').text

        def get_desc(eventsoup: BeautifulSoup) -> str:
            return eventsoup.find('small').text

        def get_date(eventsoup: BeautifulSoup) -> dt.datetime:
            cdspan = eventsoup.find('span', {'class': 'countdown'})
            timestamp = cdspan.get('data-timestamp')
            return _timestamp_to_datetime(int(timestamp))

        for event in listitems:
            if not is_event(event):
                continue

            events.append(
                rocbase.RocEvent(
                    get_name(event), get_desc(event),
                    get_date(event), is_current(event))
            )
        return events

    @classmethod
    def _get_soldier_source_table(
            cls,
            base_container: BeautifulSoup,
            basedetails: dict) -> None:
        pass

    @classmethod
    def _get_recent_activity(
            cls, base_container: BeautifulSoup,
            basedetails: dict
            ) -> list[rocbase.RocActivity]:
        recent_activity = []
        alog = base_container.find(id='activitylog_panel')
        acts = alog.findChildren('div', {'class': 'info_container'})

        for act in acts:
            children = act.findChildren(recursive=False)
            timestamp = children[0].find('span').get('data-timestamp')
            act_date = _timestamp_to_datetime(int(timestamp))
            act_text = children[1].text
            recent_activity.append(rocbase.RocActivity(act_date, act_text))

        return recent_activity

    @classmethod
    def _get_personal_totals_table(
            cls, base_container: BeautifulSoup,
            basedetails: dict
            ) -> None:
        pass

    @classmethod
    def _get_officers(
            cls, base_container: BeautifulSoup,
            basedetails: dict
            ) -> list[Tuple[str, str]]:
        pass


# TODO: FINISH THIS
class RecruitDetailsGenerator:
    @classmethod
    def generate(cls, soup: BeautifulSoup) -> rocrecruit.RecruitDetails:
        recruit_form = soup.find(id='spm_reset_form')

        spmtext = recruit_form.find('div', {'class': 'td c'}).text
        spm = int(spmtext.split(':')[1].strip())

        captchaimg = recruit_form.find(id='captcha_image')
        if captchaimg is None:
            cd = cls._get_oncooldown(recruit_form)
        else:
            cd = None

        return rocrecruit.RecruitDetails(
            soldiers_per_minute=spm,
            next_captcha_time=cd,
            requires_captcha=cd is None
        )

    @classmethod
    def _get_oncooldown(cls, recruit_form: BeautifulSoup) -> None:
        no_refresh = recruit_form.find(id='spm_no_refresh')
        resettime = no_refresh.find(
                'span', {'class': 'countdown'}).get('data-timestamp')
        return _timestamp_to_datetime(int(resettime))


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
