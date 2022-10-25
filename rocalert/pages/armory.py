import rocalert.pages.genericpages as gp
from bs4 import BeautifulSoup


class RocArmoryPage(gp.RocImageCaptchaPage):
    def __init__(self, page: BeautifulSoup) -> None:
        super().__init__(page)
        content = page.find(id='content')
        armory = content.find(id='armory')
        self._parseweapons(armory)

    def _parseweapons(self, armory: BeautifulSoup) -> None:
        self._weapons = {}

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
            self._weapons[weaponmap[i]] = gp.rocnum_to_int(count)

    def _get_weapon(self, name: str) -> int:
        return self._weapons(name)

    @property
    def daggers(self) -> int:
        return self._get_weapon('dagger')

    @property
    def mauls(self) -> int:
        return self._get_weapon('maul')

    @property
    def blades(self) -> int:
        return self._get_weapon('blade')

    @property
    def excaliburs(self) -> int:
        return self._get_weapon('excalibur')

    @property
    def sais(self) -> int:
        return self._get_weapon('sai')

    @property
    def shields(self) -> int:
        return self._get_weapon('shield')

    @property
    def mithrils(self) -> int:
        return self._get_weapon('mithril')

    @property
    def dragonskins(self) -> int:
        return self._get_weapon('dragonskin')

    @property
    def horns(self) -> int:
        return self._get_weapon('horn')

    @property
    def guard_dogs(self) -> int:
        return self._get_weapon('guard_dog')

    @property
    def torches(self) -> int:
        return self._get_weapon('torch')

    @property
    def cloaks(self) -> int:
        return self._get_weapon('cloak')

    @property
    def hooks(self) -> int:
        return self._get_weapon('hook')

    @property
    def pickaxes(self) -> int:
        return self._get_weapon('pickaxe')
