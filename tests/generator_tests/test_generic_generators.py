import unittest

from .pagehelpers import getsoup
import rocalert.models.pages.genericpages as gp
import rocalert.pagegenerators as generators


class StatsTableTest(unittest.TestCase):
    # TODO Add seperate tests for bonus tables
    def __init__(self, methodName: str = ...) -> None:
        super().__init__(methodName)

    def _getnobonustable(self) -> gp.StatTable:
        filepath = '/testpages/simplepages/statstable/statstable_nobonus.html'
        soup = getsoup(filepath)
        return generators.StatTableGenerator.generate(soup)

    def _getbonustable(self) -> gp.StatTable:
        filepath = '/testpages/simplepages/statstable/statstable_allbonus.html'
        soup = getsoup(filepath)
        return generators.StatTableGenerator.generate(soup)

    def test_simple_table_strike_val(self):
        table = self._getnobonustable()
        entry = table.strike
        self.assertTupleEqual(
            (entry.bonus, entry.action, entry.rank),
            (0, 10000000, 109),
            'Invalid strike tuple')

    def test_simple_table_defense(self):
        table = self._getnobonustable()
        entry = table.defense
        self.assertTupleEqual(
            (entry.bonus, entry.action, entry.rank),
            (0, 420690, 1),
            'Invalid defense tuple')

    def test_simple_table_spy(self):
        table = self._getnobonustable()
        entry = table.spy
        self.assertTupleEqual(
            (entry.bonus, entry.action, entry.rank),
            (0, 100001, 63),
            'Invalid strike tuple')

    def test_simple_table_sentry(self):
        table = self._getnobonustable()
        entry = table.sentry
        self.assertTupleEqual(
            (entry.bonus, entry.action, entry.rank),
            (0, 24232122, 11),
            'Invalid sentry tuple')

    def test_simple_table_kills(self):
        table = self._getnobonustable()
        self.assertEqual(
            table.kills, 322432,
            'Invalid kill count')

    def test_simple_table_killratio(self):
        table = self._getnobonustable()
        self.assertEqual(
            table.kill_ratio, 1.23,
            'Invalid kill ratio')

    def test_bonus_strike(self):
        table = self._getbonustable()
        entry = table.strike
        self.assertEqual(
            entry.bonus, 3.0,
            'Invalid strike bonus'
        )

    def test_bonus_defense(self):
        table = self._getbonustable()
        entry = table.defense
        self.assertEqual(
            entry.bonus, 55.5,
            'Invalid defense bonus'
        )

    def test_bonus_spy(self):
        table = self._getbonustable()
        entry = table.spy
        self.assertEqual(
            entry.bonus, 17.0,
            'Invalid spy bonus'
        )

    def test_bonus_sentry(self):
        table = self._getbonustable()
        entry = table.sentry
        self.assertEqual(
            entry.bonus, 1.0,
            'Invalid sentry bonus'
        )


class WeaponTroopDistTableTest(unittest.TestCase):
    # TODO Add seperate tests for with untrained table
    def __init__(self, methodName: str = ...) -> None:
        super().__init__(methodName)

    def _get_page_path(self):
        return '/testpages/simplepages/weapontrooptable/'

    def _get_untrained_table(self) -> gp.WeaponTroopDistTable:
        path = self._get_page_path() \
            + 'weapontrooptable_hasuntrained.html'
        soup = getsoup(path)
        return generators.WeaponTroopDistTableGenerator.generate(soup)

    def _get_no_untrained_table(self) -> gp.WeaponTroopDistTable:
        path = '/testpages/simplepages/weapontrooptable/' \
            + 'weapontrooptable_nountrained.html'
        soup = getsoup(path)
        return generators.WeaponTroopDistTableGenerator.generate(soup)

    def _get_training_unt_table(self) -> gp.WeaponTroopDistTable:
        path = self._get_page_path() + 'weapontrooptable_training_unt.html'
        soup = getsoup(path)
        return generators.WeaponTroopDistTableGenerator.generate(soup)

    def test_load_training_table(self):
        self._get_training_unt_table()

    def test_nountrained_attack(self):
        table = self._get_no_untrained_table()
        entry = table.attack_wt_dist

        self.assertTupleEqual(
            (entry.soldiers, entry.weapon_count),
            (2322121, 1234),
            'Invalid attack weapon troop distribution'
        )

    def test_nountrained_defense(self):
        table = self._get_no_untrained_table()
        entry = table.defense_wt_dist

        self.assertTupleEqual(
            (entry.soldiers, entry.weapon_count),
            (360885, 36333),
            'Invalid defense weapon troop distribution'
        )

    def test_nountrained_spy(self):
        table = self._get_no_untrained_table()
        entry = table.spy_wt_dist

        self.assertTupleEqual(
            (entry.soldiers, entry.weapon_count),
            (3221, 20),
            'Invalid spy weapon troop distribution'
        )

    def test_nountrained_sentry(self):
        table = self._get_no_untrained_table()
        entry = table.sentry_wt_dist

        self.assertTupleEqual(
            (entry.soldiers, entry.weapon_count),
            (311483, 304814),
            'Invalid sentry weapon troop distribution'
        )

    def test_nountrained_untrained(self):
        table = self._get_no_untrained_table()
        entry = table.untrained_soldiers

        self.assertTupleEqual(
            (entry.soldiers, entry.weapon_count),
            (0, None),
            'Invalid untrained weapon troop distribution'
        )

    def test_nountrained_tff(self):
        table = self._get_no_untrained_table()
        entry = table.total_fighting_force

        self.assertTupleEqual(
            (entry.soldiers, entry.weapon_count),
            (1684268, None),
            'Invalid tff weapon troop distribution'
        )

    def test_nountrained_tcf(self):
        table = self._get_no_untrained_table()
        entry = table.total_covert_force

        self.assertTupleEqual(
            (entry.soldiers, entry.weapon_count),
            (311503, None),
            'Invalid tcf weapon troop distribution'
        )

    def test_untrained_untrained(self):
        table = self._get_untrained_table()
        entry = table.untrained_soldiers

        self.assertTupleEqual(
            (entry.soldiers, entry.weapon_count),
            (1120, None),
            'Invalid untrained soldier count (untrained)'
        )
