import unittest

from .pagehelpers import getsoup
import rocalert.models as rocmodels
import rocalert.pagegenerators as generators


class ArmoryPageTest(unittest.TestCase):
    def __init__(self, methodName: str = ...) -> None:
        super().__init__(methodName)

    def _get_page_path(self):
        return '/testpages/armory/'

    def _get_basic_armory(self) -> rocmodels.ArmoryModel:
        path = self._get_page_path() + 'armorybasic.html'
        soup = getsoup(path)
        return generators.ArmoryDetailsGenerator.generate(soup)

    def test_attack_weapon_zero_count_correct(self):
        details = self._get_basic_armory()
        self.assertTupleEqual(
            (details.dagger.count, details.maul.count,
             details.blade.count, details.excalibur.count),
            (0, 0, 0, 0)
        )

    def test_defense_weapon_count_correct(self):
        details = self._get_basic_armory()
        self.assertTupleEqual(
            (details.sai.count, details.shield.count,
             details.mithril.count, details.dragonskin.count),
            (0, 1144166, 1318428, 20)
        )

    def test_spy_weapon_count_correct(self):
        details = self._get_basic_armory()
        self.assertTupleEqual(
            (details.cloak.count, details.hook.count, details.pickaxe.count),
            (4754, 216826, 24032),
        )

    def test_sentry_weapon_count_correct(self):
        details = self._get_basic_armory()
        self.assertTupleEqual(
            (details.horn.count, details.guard_dog.count, details.torch.count),
            (9387, 612738, 253898)
        )

    def test_attack_weapon_cost_correct(self):
        details = self._get_basic_armory()
        self.assertTupleEqual(
            (details.dagger.cost, details.maul.cost,
             details.blade.cost, details.excalibur.cost),
            (1000, 15000, 200000, 1000000)
        )

    def test_defense_weapon_cost_correct(self):
        details = self._get_basic_armory()
        self.assertTupleEqual(
            (details.sai.cost, details.shield.cost,
             details.mithril.cost, details.dragonskin.cost),
            (1000, 15000, 200000, 1000000)
        )

    def test_spy_weapon_cost_correct(self):
        details = self._get_basic_armory()
        self.assertTupleEqual(
            (details.cloak.cost, details.hook.cost, details.pickaxe.cost),
            (50000, 100000, 300000),
        )

    def test_sentry_weapon_cost_correct(self):
        details = self._get_basic_armory()
        self.assertTupleEqual(
            (details.horn.cost, details.guard_dog.cost, details.torch.cost),
            (50000, 100000, 300000)
        )
