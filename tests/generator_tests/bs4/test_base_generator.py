import unittest

from .pagehelpers import getsoup
import rocalert.models.pages.base as rocbase
import rocalert.pagegenerators.bs4 as generators
import tests.generator_tests.pagepaths as pagepaths


class BasePageTest(unittest.TestCase):
    def _get_dubtrub_page(self) -> rocbase.BaseDetails:
        path = pagepaths.Base.DUB_TRUB
        soup = getsoup(path)
        return generators.BaseDetailsGenerator.generate(soup)

    def _get_stoleturn_page(self) -> rocbase.BaseDetails:
        path = pagepaths.Base.STOLE_TURN
        soup = getsoup(path)
        return generators.BaseDetailsGenerator.generate(soup)

    def _get_basewithofficers_page(self) -> rocbase.BaseDetails:
        path = pagepaths.Base.BASE_WITH_OFFICERS
        soup = getsoup(path)
        return generators.BaseDetailsGenerator.generate(soup)

    def _get_basefoundbrokenkey_page(self) -> rocbase.BaseDetails:
        path = pagepaths.Base.FOUND_BROKE_KEY
        soup = getsoup(path)
        return generators.BaseDetailsGenerator.generate(soup)

    def _get_noactive_events_page(self) -> rocbase.BaseDetails:
        path = pagepaths.Base.NO_ACTIVE_EVENTS
        soup = getsoup(path)
        return generators.BaseDetailsGenerator.generate(soup)

    def test_dubtrub(self):
        details = self._get_dubtrub_page()

        self.assertEqual(
            len(details.current_events),
            1,
            'Incorrect number of current events on dubtrub page'
        )

        self.assertEqual(
            len(details.upcoming_events),
            2,
            'Incorrect number of upcoming events on dubtrub page'
        )

        self.assertEqual(
            details.current_events[0].name,
            'Double Trouble',
            'Incorrect current event name on dubtrub page'
        )

    def test_stoleturns(self):
        details = self._get_stoleturn_page()

        self.assertIsNotNone(
            details.recent_activity,
            'Recent activity should not be none'
        )
        self.assertEqual(
            len(details.recent_activity),
            10,
            'recent activity list is not correct length'
        )
        self.assertEqual(
            'stole' in details.recent_activity[7].activity_text,
            True,
            '7th activity text should be user stealing turns.'
        )

    def test_totals_table(self):
        pass

    def test_alliance(self):
        pass

    def test_officers(self):
        pass

    def test_commandchain(self):
        pass

    def test_serverdate(self):
        pass

    def test_soldier_source(self):
        pass
