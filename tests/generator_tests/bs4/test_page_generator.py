import unittest

from .pagehelpers import getsoup
import rocalert.models.pages.genericpages as gp
import rocalert.pagegenerators.bs4 as generators
import tests.generator_tests.pagepaths as pagepaths


class PageLoggedInTest(unittest.TestCase):
    def _get_simple_loggedout_page(self) -> gp.RocPage:
        path = pagepaths.SimplePages.NOT_LOGGED_IN
        soup = getsoup(path)
        return generators.page.PageGenerator.generate(soup)

    def _get_simple_loggedin_page(self) -> gp.RocPage:
        path = pagepaths.SimplePages.LOGGED_IN_PAGE
        soup = getsoup(path)
        return generators.page.PageGenerator.generate(soup)

    def test_logged_in(self):
        page = self._get_simple_loggedin_page()
        self.assertTrue(page.logged_in, 'Page is not logged in.')

    def test_notlogged_in(self):
        page = self._get_simple_loggedout_page()
        self.assertFalse(page.logged_in, 'Page is logged in.')


class PageTypeDetectorTest(unittest.TestCase):
    pass


class RocCooldownPageTest(unittest.TestCase):
    def __init__(self, methodName: str = ...) -> None:
        super().__init__(methodName)
    # TODO add tests


class RocImageCaptchaPageTest(unittest.TestCase):
    def __init__(self, methodName: str = ...) -> None:
        super().__init__(methodName)

    # TODO add tests

