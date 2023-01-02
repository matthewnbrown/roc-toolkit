from bs4 import BeautifulSoup

from rocalert.pagegenerators import ROCPageGeneratorABC,\
    PageGenerationException
from rocalert.logging import DateTimeGeneratorABC
import rocalert.models as rocmodels
import rocalert.enums as rocenums
import rocalert.models.pages.genericpages as gp
import rocalert.models.pages.armory as rocarmory
import rocalert.models.pages.keep as rockeep
import rocalert.models.pages.base as rocbase
import rocalert.models.pages.recruit as rocrecruit
import rocalert.models.pages.training as roctraining
import rocalert.pagegenerators.bs4 as pagegenerators


_page_type_class_map = {
    rocenums.RocPageType.BASE: rocbase.BasePage,
    rocenums.RocPageType.TRAINING: roctraining.TrainingPage,
    rocenums.RocPageType.ARMORY: rocarmory.ArmoryPage,
    rocenums.RocPageType.RECRUIT: rocrecruit.RecruitPage,
    rocenums.RocPageType.KEEP: rockeep.KeepPage,
}


class BeautifulSoupPageTypeDetector:
    _TITLE_TOPAGE_MAP = {
        'Recruit Center': rocenums.RocPageType.RECRUIT,
        'Training': rocenums.RocPageType.TRAINING,
        'Armory': rocenums.RocPageType.ARMORY,
        'Buildings': rocenums.RocPageType.BUILDINGS_AND_SKILLS,
        'Activity Log': rocenums.RocPageType.ACTIVITY_LOG,
        'Battlefield': rocenums.RocPageType.BATTLEFIELD,
        'Attack Log': rocenums.RocPageType.ATTACK_LOG,
        'Intel': rocenums.RocPageType.INTEL_FILES,
        'Covert Action Report': rocenums.RocPageType.INTEL_DETAIL,
        'Messages': rocenums.RocPageType.MAIL,
        'More fun than you can shake a pointy pickaxe at': rocenums.RocPageType.HOME  # noqa: E501
    }

    @classmethod
    def detect_page_type(cls, pagesoup: BeautifulSoup) -> rocenums.RocPageType:
        loggedin = pagesoup.find(id='login_form') is None

        if not loggedin:
            return cls.get_not_loggedin_pagetype(pagesoup)

        if pagesoup.find(id='base_container') is not None:
            return rocenums.RocPageType.BASE

        title_pagetype = cls.try_get_pagetype_from_title(pagesoup)

        if title_pagetype is not rocenums.RocPageType.UNKNOWN:
            return title_pagetype

        return rocenums.RocPageType.UNKNOWN

    @classmethod
    def get_not_loggedin_pagetype(cls, pagesoup: BeautifulSoup
                                  ) -> rocenums.RocPageType:
        content = pagesoup.find(id='content')

        join_header = content.find('div', {'class': 'join_header'})
        if join_header is not None:
            return rocenums.RocPageType.HOME

        login_error = content.find('h1', {'class': 'stoptitle'})
        if login_error is not None and login_error.text == 'Login':
            return rocenums.RocPageType.LOGIN_REQUEST_ERROR

        return rocenums.RocPageType.UNKNOWN

    @classmethod
    def try_get_pagetype_from_title(cls, pagesoup: BeautifulSoup
                                    ) -> rocenums.RocPageType:
        titlesoup = pagesoup.find('title')
        if titlesoup is None:
            return None

        _, title = titlesoup.text.split(':', maxsplit=1)
        title = title.strip()

        if title in cls._TITLE_TOPAGE_MAP:
            return cls._TITLE_TOPAGE_MAP[title]

        if title.startswith('Stats for'):
            return rocenums.RocPageType.TARGET_STATS
        if title.startswith('Attack '):
            return rocenums.RocPageType.TARGET_ATTACK
        if title.startswith('Probe '):
            return rocenums.RocPageType.TARGET_PROBE
        if title.startswith('Recon '):
            return rocenums.RocPageType.TARGET_RECON
        if title.startswith('Sabotage '):
            return rocenums.RocPageType.TARGET_SABOTAGE
        if title.startswith('Spite '):
            return rocenums.RocPageType.TARGET_SPITE
        if title.endswith('\'s Keep'):
            return rocenums.RocPageType.KEEP

        return rocenums.RocPageType.UNKNOWN


class BeautifulSoupPageGenerator(ROCPageGeneratorABC):
    def __init__(
            self,
            parser: str,
            timegenerator: DateTimeGeneratorABC
    ) -> None:
        self._parser = parser
        self._timegenerator = timegenerator
        self._pagetypedetector = BeautifulSoupPageTypeDetector

    def generate(self, pagehtml: str) -> gp.RocPage:
        soup = BeautifulSoup(pagehtml, self._parser)
        pagetype = self._pagetypedetector.detect_page_type(soup)

        match pagetype:
            case rocenums.RocPageType.BASE:
                page = self._generate_base(soup)
            case rocenums.RocPageType.TRAINING:
                page = self._generate_training(soup)
            case rocenums.RocPageType.ARMORY:
                page = self._generate_armory(soup)
            case rocenums.RocPageType.RECRUIT:
                page = self._generate_recruit(soup)
            case rocenums.RocPageType.KEEP:
                page = self._generate_keep(soup)
            case _:
                raise PageGenerationException(
                    f'Unknown page type during parsing: {pagetype}'
                )

        page.page_type = pagetype
        page.creation_date = self._timegenerator.get_current_time()
        page.logged_in = self._is_loggedin(soup)

        pageclass = _page_type_class_map[pagetype]
        if issubclass(pageclass, gp.ClockBarPage):
            page.clock_bar = self._get_clockbar(soup)
        if issubclass(pageclass, gp.CaptchaPage):
            page.captcha_hash = self._get_captchahash(soup)

        return page

    def _get_clockbar(self, pagesoup: BeautifulSoup) -> gp.ClockBar:
        return pagegenerators.ClockBarGenerator.generate(
            pagesoup, self._timegenerator)

    @staticmethod
    def _get_captchahash(pagesoup: BeautifulSoup) -> str:
        captchasoup = pagesoup.find(id='captcha_image')

        if captchasoup is None:
            return None
        return captchasoup.get('src').split('=')[1]

    @staticmethod
    def _generate_base(soup: BeautifulSoup) -> rocbase.BasePage:
        details = pagegenerators.BaseDetailsGenerator.generate(soup)
        base_container = soup.find(id='base_container')

        stsoup = base_container.find(
            id='militaryeffectiveness_panel').find('table')
        stattable = pagegenerators.stattable.StatTableGenerator.generate(
            stsoup
        )
        weapondist = pagegenerators.WeaponTroopDistTableGenerator.generate(
            base_container.find(id='weaponsandtroops_panel').find('table')
        )

        return rocbase.BasePage(base=details,
                                stat_table=stattable,
                                weapon_dist_table=weapondist)

    @staticmethod
    def _generate_training(soup: BeautifulSoup) -> roctraining.TrainingPage:
        content = soup.find(id='content')
        fpctables = content.find_all(
            'div', {'class': 'flexpanel_container'})[1].find_all('table')
        stsoup = fpctables[0]
        stattable = pagegenerators.stattable.StatTableGenerator.generate(
            stsoup
        )
        wtsoup = fpctables[2]
        wtdist = pagegenerators.WeaponTroopDistTableGenerator.generate(
            table=wtsoup)
        details = pagegenerators.TrainingDetailsGenerator.generate(soup=soup)

        return roctraining.TrainingPage(
            training=details,
            weapon_dist_table=wtdist,
            stat_table=stattable
        )

    @staticmethod
    def _generate_armory(soup: BeautifulSoup) -> rocarmory.ArmoryPage:
        details = pagegenerators.ArmoryDetailsGenerator.generate(
            soup=soup
        )

        tablecontainer = soup.find(id='content').findChildren(
            'div', {'class': 'flexpanel_container'}, recursive=False)[0]
        tables = tablecontainer.find_all('table')

        stattable = pagegenerators.StatTableGenerator.generate(table=tables[0])
        wtdist = pagegenerators.WeaponTroopDistTableGenerator.generate(
            table=tables[1])

        return rocarmory.ArmoryPage(
            armory=details,
            stat_table=stattable,
            weapon_dist_table=wtdist
        )

    @staticmethod
    def _generate_recruit(soup: BeautifulSoup) -> rocrecruit.RecruitPage:
        details = pagegenerators.RecruitDetailsGenerator.generate(soup=soup)
        return rocrecruit.RecruitPage(
            recruit=details
        )

    @staticmethod
    def _generate_keep(soup: BeautifulSoup) -> rockeep.KeepPage:
        details = pagegenerators.KeepStatusGenerator.generate(soup=soup)
        return rockeep.KeepPage(keep=details)

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
