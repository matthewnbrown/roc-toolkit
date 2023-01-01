from bs4 import BeautifulSoup
import dataclasses

import rocalert.models.pages.genericpages as gp
import rocalert.models as rocmodels


def _dataclass_from_dict(klass, d):
    try:
        fieldtypes = {f.name: f.type for f in dataclasses.fields(klass)}
        return klass(**{f: _dataclass_from_dict(
            fieldtypes[f], d[f]) for f in d})
    except: # noqa E722
        return d  # Not a dataclass field


class ArmoryDetailsGenerator:
    @classmethod
    def generate(cls, soup: BeautifulSoup) -> rocmodels.ArmoryModel:
        content = soup.find(id='content')
        armory = content.find(id='armory')
        weaponmap = cls._parseweapons_map(armory)

        armorymodel = _dataclass_from_dict(rocmodels.ArmoryModel, weaponmap)
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
