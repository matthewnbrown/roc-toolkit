import unittest
from bs4 import BeautifulSoup

from rocalert.pages import RocPage


def _get_dir():
    return __file__[:__file__.rfind('\\')+1]


class PageLoggedInTest(unittest.TestCase):
    def __init__(self, methodName: str = ...) -> None:
        super().__init__(methodName)

    def test_logged_in(self):
        filepath = _get_dir() + '/testpages/loginstatus/true.html'
        with open(filepath) as f:
            text = f.read()
            soup = BeautifulSoup(text, 'html.parser')

        page = RocPage(soup)
        self.assertTrue(page.logged_in, 'Page is not logged in.')

    def test_notlogged_in(self):
        filepath = _get_dir() + '/testpages/loginstatus/false.html'

        with open(filepath) as f:
            text = f.read()
            soup = BeautifulSoup(text, 'html.parser')

        page = RocPage(soup)
        self.assertFalse(page.logged_in, 'Page is logged in.')
