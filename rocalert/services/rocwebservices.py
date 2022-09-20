from typing import Dict, List
from bs4 import BeautifulSoup
from rocalert.roc_web_handler import RocWebHandler
from rocalert.rocaccount import BattlefieldTarget


class BattlefieldPageService():

    @classmethod
    def run_service(cls, roc: RocWebHandler, pagenum: int) -> Dict:
        pageurl = roc.site_settings['roc_home'] + \
            f'/battlefield.php?p={pagenum}'

        roc.go_to_page(pageurl)

        soup = BeautifulSoup(roc.r.text, 'html.parser')
        content = soup.find('div', id='content')

        if not cls._checkvalidpage(content, pagenum):
            return {
                'response': 'error',
                'error': f'Invalid page number {pagenum}'}

        players = content.find('ul')

        targets = cls._get_alltargets(players)

        return {
            'response': 'success',
            'result': targets
        }

    @classmethod
    def _checkvalidpage(cls, content: BeautifulSoup, pagenum: int) -> bool:
        pagerangetext = content.contents[1].contents[1].text
        usercount = int(pagerangetext[pagerangetext.index('(') + 1:
                        pagerangetext(')')])
        pagecount = usercount//50 if usercount % 50 == 0 else \
            1 + usercount % 50

        return 1 <= pagenum <= pagecount

    @classmethod
    def _get_alltargets(cls,
                        players: BeautifulSoup
                        ) -> List[BattlefieldTarget]:
        pass

    @classmethod
    def _get_bftarget(cls, usercontent: BeautifulSoup) -> BattlefieldTarget:
        pass
