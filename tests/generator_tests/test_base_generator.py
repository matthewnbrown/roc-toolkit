import unittest

from .pagehelpers import getsoup
import rocalert.models.pages.base as rocbase
import rocalert.pagegenerators as generators


class BasePageTest(unittest.TestCase):
    def __init__(self, methodName: str = ...) -> None:
        super().__init__(methodName)
        self._pagepath = '/testpages/base/'

    def _get_dubtrub_page(self) -> rocbase.BaseDetails:
        path = self._pagepath + 'dubtrub.html'
        soup = getsoup(path)
        return generators.BaseDetailsGenerator.generate(soup)

    def _get_stoleturn_page(self) -> rocbase.BaseDetails:
        path = self._pagepath + 'stoleturn.html'
        soup = getsoup(path)
        return generators.BaseDetailsGenerator.generate(soup)

    def _get_basewithofficers_page(self) -> rocbase.BaseDetails:
        path = self._pagepath + 'basewithofficers.html'
        soup = getsoup(path)
        return generators.BaseDetailsGenerator.generate(soup)

    def _get_basefoundbrokenkey_page(self) -> rocbase.BaseDetails:
        path = self._pagepath + 'basefoundbrokenkey.html'
        soup = getsoup(path)
        return generators.BaseDetailsGenerator.generate(soup)

    def _get_noactive_events_page(self) -> rocbase.BaseDetails:
        path = self._pagepath + 'base_noactive_events.html'
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
