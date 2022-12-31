from bs4 import BeautifulSoup

import rocalert.models.pages.genericpages as gp


class TurnBoxGenerator:
    @classmethod
    def generate(cls, pagesoup: BeautifulSoup) -> gp.TurnBoxPage:
        pass
