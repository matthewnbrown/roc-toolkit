import unittest

from .pagehelpers import getsoup
import rocalert.models.pages.keep as rockeep
import rocalert.pagegenerators.bs4 as generators


class KeepPageTest(unittest.TestCase):
    def __init__(self, methodName: str = ...) -> None:
        super().__init__(methodName)
        self._pagepath = '/testpages/keep/'

    def _get_6k_0b_rep_pagedetails(self) -> rockeep.KeepDetails:
        path = self._pagepath + '6k0brep.html'
        soup = getsoup(path)
        return generators.KeepStatusGenerator.generate(soup)

    def test_keycount(self):
        details = self._get_6k_0b_rep_pagedetails()

        self.assertEqual(
            details.key_count,
            6,
            'Unbroken key count does not match expected value'
        )

    def test_6k_0b_rep(self):
        details = self._get_6k_0b_rep_pagedetails()

        self.assertEqual(
            details.broken_key_count,
            0,
            'Broken key count does not match expect value of zero'
        )

    # TODO: Get test pages and implement test cases

    def test_6k_0b_norep(self):
        pass

    def test_0k_1b_norep(self):
        pass

    def test_0k_1b_rep(self):
        pass

    def test_0k_0b_norep(self):
        pass

    def test_0k_0b_rep(self):
        pass

    def test_1k_1b_rep(self):
        pass

    def test_1k_1b_norep(self):
        pass
