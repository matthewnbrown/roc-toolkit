from typing import Dict, Iterable, List
from bs4 import BeautifulSoup
from rocalert.roc_web_handler import RocWebHandler
from rocalert.rocaccount import BattlefieldTarget


def _cleanstr_to_int(num: str) -> int:
    return int(num.strip().replace(',', ''))


class BattlefieldPageService():

    @classmethod
    def run_service(cls, roc: RocWebHandler, pagenum: int) -> dict:
        pageurl = roc.site_settings['roc_home'] + \
            f'/battlefield.php?p={pagenum}'

        roc.go_to_page(pageurl)

        soup = BeautifulSoup(roc.r.text, 'html.parser')
        content = soup.find('div', id='content')

        if not cls._checkvalidpage(content, pagenum):
            return {
                'response': 'error',
                'error': f'Invalid page number {pagenum}'}

        players = content.find('ul', {'class', 'players'}) \
            .findChildren(recursive=False)

        targets = cls._get_alltargets(players)

        return {
            'response': 'success',
            'result': targets
        }

    @classmethod
    def _checkvalidpage(cls, content: BeautifulSoup, pagenum: int) -> bool:
        pagerangetext = content.contents[1].contents[1].text
        usercount = int(pagerangetext[pagerangetext.index('(') + 1:
                        pagerangetext.index(')')])
        pagecount = usercount//50 if usercount % 50 == 0 else \
            1 + usercount // 50

        return 1 <= pagenum <= pagecount

    @classmethod
    def _get_alltargets(cls,
                        players: Iterable
                        ) -> List[BattlefieldTarget]:
        result = []

        for playitem in players:

            player = cls._get_bftarget(playitem)

            result.append(player)

        return result

    @classmethod
    def _get_bftarget(cls, usercontent: BeautifulSoup) -> BattlefieldTarget:
        id = usercontent.get('id').split('_')[1]

        children = usercontent.find_all('div', recursive=False)

        rank = children[0].get('id').split('_')[1]
        name_alli = children[1].find_all('a')
        name = name_alli[0].text
        alliance = None if len(name_alli) <= 1 else name_alli[1].text

        tff_gold = children[2].find_all('div', recursive=False)
        tfftext = tff_gold[0].text.strip().split(' ')

        tff = _cleanstr_to_int(tfftext[0])
        tfftype = tfftext[1]

        gold = None if '?' in tff_gold[1].text else \
            _cleanstr_to_int(tff_gold[1].text.strip().split(' ')[0])

        return BattlefieldTarget(id, rank, name, alliance, tff, tfftype, gold)
