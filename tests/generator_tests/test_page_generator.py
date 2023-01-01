import unittest

from .pagehelpers import getsoup
import rocalert.models.pages.genericpages as gp
import rocalert.pagegenerators.bs4 as generators


class PageLoggedInTest(unittest.TestCase):
    def __init__(self, methodName: str = ...) -> None:
        super().__init__(methodName)

    def _get_simple_loggedout_page(self) -> gp.RocPage:
        path = '/testpages/simplepages/loginstatus/true.html'
        soup = getsoup(path)
        return generators.page.PageGenerator.generate(soup)

    def _get_simple_loggedin_page(self) -> gp.RocPage:
        path = '/testpages/simplepages/loginstatus/false.html'
        soup = getsoup(path)
        return generators.page.PageGenerator.generate(soup)

    def test_logged_in(self):
        page = self._get_simple_loggedin_page()
        self.assertTrue(page.logged_in, 'Page is not logged in.')

    def test_notlogged_in(self):
        page = self._get_simple_loggedout_page()
        self.assertFalse(page.logged_in, 'Page is logged in.')


class RocCooldownPageTest(unittest.TestCase):
    def __init__(self, methodName: str = ...) -> None:
        super().__init__(methodName)
    # TODO add tests


class RocImageCaptchaPageTest(unittest.TestCase):
    def __init__(self, methodName: str = ...) -> None:
        super().__init__(methodName)

    # TODO add tests
