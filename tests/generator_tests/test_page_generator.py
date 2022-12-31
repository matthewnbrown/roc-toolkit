import unittest

from .pagehelpers import getsoup
import rocalert.models.pages.genericpages as gp


class PageLoggedInTest(unittest.TestCase):
    def __init__(self, methodName: str = ...) -> None:
        super().__init__(methodName)

    def test_logged_in(self):
        path = '/testpages/simplepages/loginstatus/true.html'
        soup = getsoup(path)

        page = gp.RocPage(soup)
        self.assertTrue(page.logged_in, 'Page is not logged in.')

    def test_notlogged_in(self):
        path = '/testpages/simplepages/loginstatus/false.html'
        soup = getsoup(path)

        page = gp.RocPage(soup)
        self.assertFalse(page.logged_in, 'Page is logged in.')


class RocCooldownPageTest(unittest.TestCase):
    def __init__(self, methodName: str = ...) -> None:
        super().__init__(methodName)
    # TODO add tests


class RocImageCaptchaPageTest(unittest.TestCase):
    def __init__(self, methodName: str = ...) -> None:
        super().__init__(methodName)

    # TODO add tests
