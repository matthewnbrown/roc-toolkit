from typing import List
from bs4 import BeautifulSoup
from rocalert.roc_web_handler import RocWebHandler


class BattlefieldPageService():

    @classmethod
    def run_service(cls, roc: RocWebHandler, pagenum: int) -> List:
        pageurl = roc.site_settings['roc_home'] + \
            f'/battlefield.php?p={pagenum}'

        roc.go_to_page(pageurl)

        soup = BeautifulSoup(roc.r.text, 'html.parser')
        content = soup.find('div', id='content')

        if not cls._checkvalidpage(content, pagenum):
            return {
                'response': 'error',
                'error': f'Invalid page number {pagenum}'}

    @classmethod
    def _checkvalidpage(cls, content: BeautifulSoup, pagenum: int) -> bool:
        pagerangetext = content.contents[1].contents[1].text
        usercount = int(pagerangetext[pagerangetext.index('(') + 1:
                        pagerangetext(')')])
        pagecount = usercount//50 if usercount % 50 == 0 else \
            1 + usercount % 50

        return 1 <= pagenum <= pagecount
