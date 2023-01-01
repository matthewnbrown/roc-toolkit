import unittest

from .pagehelpers import getsoup
import rocalert.models.pages.training as roctraining
import rocalert.pagegenerators.bs4 as generators


class TrainingPageTest(unittest.TestCase):
    def __init__(self, methodName: str = ...) -> None:
        super().__init__(methodName)
        self._pagepath = '/testpages/training/'

    def _get_allmercs_pagedetails(self) -> roctraining.TrainingDetails:
        path = self._pagepath + 'trainingallmercs.html'
        soup = getsoup(path)
        return generators.TrainingDetailsGenerator.generate(soup)

    def _get_0am_pagedetails(self) -> roctraining.TrainingDetails:
        path = self._pagepath + 'training0am.html'
        soup = getsoup(path)
        return generators.TrainingDetailsGenerator.generate(soup)

    def _get_none_avail_mercsdetails(self) -> roctraining.TrainingDetails:
        path = self._pagepath + 'training_none_avail.html'
        soup = getsoup(path)
        return generators.TrainingDetailsGenerator.generate(soup)

    def test_allmercs_values(self):
        details = self._get_allmercs_pagedetails()

        self.assertTupleEqual(
            (details.attack_mercenaries.count,
             details.attack_mercenaries.income),
            (2, -20),
            'Incorrect attack mercs pair'
        )

        self.assertTupleEqual(
            (details.defense_mercenaries.count,
             details.defense_mercenaries.income),
            (107630, -1076300),
            'Incorrect defense merc pair'
        )

        self.assertTupleEqual(
            (details.untrained_mercenaries.count,
             details.untrained_mercenaries.income),
            (69555, -347775),
            'Inccorect defense merc pair'
        )

    def test_0am_values(self):
        details = self._get_0am_pagedetails()

        self.assertTupleEqual(
            (details.attack_mercenaries.count,
             details.attack_mercenaries.income),
            (0, 0),
            'Incorrect attack mercs pair'
        )

        self.assertTupleEqual(
            (details.defense_mercenaries.count,
             details.defense_mercenaries.income),
            (107630, -1076300),
            'Incorrect defense merc pair'
        )

        self.assertTupleEqual(
            (details.untrained_mercenaries.count,
             details.untrained_mercenaries.income),
            (69555, -347775),
            'Incorrect defense merc pair'
        )

    def test_allmercs_availmercs(self):
        details = self._get_allmercs_pagedetails()

        self.assertTupleEqual(
            (details.avail_attack_mercs.count,
             details.avail_attack_mercs.income),
            (104653, 2500),
            'Incorrect number/cost of attack mercenaries'
        )

        self.assertTupleEqual(
            (details.avail_defense_mercs.count,
             details.avail_defense_mercs.income),
            (114653, 2500),
            'Incorrect number/cost of defense mercenaries'
        )

        self.assertTupleEqual(
            (details.avail_untrained_mercs.count,
             details.avail_untrained_mercs.income),
            (114653, 2000),
            'Incorrect number/cost of untrained mercenaries'
        )

    def test_none_avail_merccount(self):
        details = self._get_none_avail_mercsdetails()

        self.assertTupleEqual(
            (details.avail_attack_mercs.count,
             details.avail_defense_mercs.count,
             details.avail_untrained_mercs.count),
            (50664, 0, 0),
            'Incorrect amount of mercenaries'
        )

    def test_event_merc_cost(self):
        details = self._get_none_avail_mercsdetails()

        self.assertTupleEqual(
            (details.avail_untrained_mercs.income,
             details.avail_defense_mercs.income,
             details.avail_untrained_mercs.income),
            (577, 577, 577),
            'Incorrect cost of mercenaries during event'
        )

    def test_attack_soldier_costs(self):
        details = self._get_allmercs_pagedetails()

        self.assertEqual(
            details.attack_sold_cost,
            1000
        )

    def test_defense_soldier_costs(self):
        details = self._get_allmercs_pagedetails()

        self.assertEqual(
            details.defense_sold_cost,
            1500
        )

    def test_spy_costs(self):
        details = self._get_allmercs_pagedetails()

        self.assertEqual(
            details.spy_sold_cost,
            2500
        )

    def test_sentry_cost(self):
        details = self._get_allmercs_pagedetails()

        self.assertEqual(
            details.sentry_sold_cost,
            3000
        )
