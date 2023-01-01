from bs4 import BeautifulSoup

from .page import ROCPageGeneratorABC, PageGenerationException
from rocalert.logging import DateTimeGeneratorABC
import rocalert.models as rocmodels  # noqa f401
import rocalert.enums as rocenums
import rocalert.models.pages.genericpages as gp
import rocalert.models.pages.armory as rocarmory
import rocalert.models.pages.keep as rockeep
import rocalert.models.pages.base as rocbase
import rocalert.models.pages.recruit as rocrecruit
import rocalert.models.pages.training as roctraining
import rocalert.pagegenerators as pagegenerators


_page_type_class_map = {
    rocenums.RocPageType.BASE: rocbase.BasePage,
    rocenums.RocPageType.TRAINING: roctraining.TrainingPage,
    rocenums.RocPageType.ARMORY: rocarmory.ArmoryPage,
    rocenums.RocPageType.RECRUIT: rocrecruit.RecruitPage,
    rocenums.RocPageType.KEEP: rockeep.KeepPage,
}


class BeautifulSoupPageGenerator(ROCPageGeneratorABC):
    def __init__(
            self,
            parser: str,
            timegenerator: DateTimeGeneratorABC
            ) -> None:
        self._parser = parser
        self._timegenerator = timegenerator

    def generate(self, pagehtml: str) -> gp.RocPage:
        soup = BeautifulSoup(pagehtml, self._parser)
        pagetype = self._detect_pagetype(soup)

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

        pageclass = _page_type_class_map[pagetype]
        if issubclass(pageclass, gp.ClockBarPage):
            page.clock_bar = self._get_clockbar(soup)
        if issubclass(pageclass, gp.CaptchaPage):
            page.captcha_hash = self._get_captchahash(soup)

        page.page_type = pagetype
        page.creation_date = self._timegenerator.get_current_time()
        page.logged_in = self._is_loggedin(soup)

    @staticmethod
    def _get_clockbar(
            pagesoup: BeautifulSoup
            ) -> pagegenerators.ClockBarGenerator:
        pass

    @staticmethod
    def _get_captchahash(pagesoup: BeautifulSoup) -> str:
        pass

    @staticmethod
    def _detect_pagetype(soup: BeautifulSoup) -> rocenums.RocPageType:
        pass

    @staticmethod
    def _generate_base(soup: BeautifulSoup) -> rocbase.BasePage:
        return rocbase.BasePage()

    @staticmethod
    def _generate_training(soup: BeautifulSoup) -> roctraining.TrainingPage:
        return roctraining.TrainingPage()

    @staticmethod
    def _generate_armory(soup: BeautifulSoup) -> rocarmory.ArmoryPage:
        return rocarmory.ArmoryPage()

    @staticmethod
    def _generate_recruit(soup: BeautifulSoup) -> rocrecruit.RecruitPage:
        return rocrecruit.RecruitPage()

    @staticmethod
    def _generate_keep(soup: BeautifulSoup) -> rockeep.KeepPage:
        return rockeep.KeepPage()

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
