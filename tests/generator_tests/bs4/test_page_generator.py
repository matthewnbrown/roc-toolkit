import unittest

from .pagehelpers import getsoup
import rocalert.models.pages.genericpages as gp
import rocalert.pagegenerators.bs4 as generators
import rocalert.enums as rocenums
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
    def __init__(self, methodName: str = ...) -> None:
        super().__init__(methodName)
        self.detector = generators.bs4souppage.BeautifulSoupPageTypeDetector

    def get_type_from_path(self, path):
        page = getsoup(path)
        return self.detector.detect_page_type(page)

    def test_recruit_detection(self):
        pagetype = self.get_type_from_path(pagepaths.Recruit.HAS_CAPTCHA)

        self.assertEqual(
            pagetype,
            rocenums.RocPageType.RECRUIT
        )

    def test_base_detection(self):
        pagetype = self.get_type_from_path(pagepaths.Base.DUB_TRUB)

        self.assertEqual(
            pagetype,
            rocenums.RocPageType.BASE
        )

    def test_armory_detection(self):
        pagetype = self.get_type_from_path(pagepaths.Armory.BASIC)

        self.assertEqual(
            pagetype,
            rocenums.RocPageType.ARMORY
        )

    def test_training_detection(self):
        pagetype = self.get_type_from_path(pagepaths.Training.ALL_MERCS)

        self.assertEqual(
            pagetype,
            rocenums.RocPageType.TRAINING
        )

    def test_login_errorpage_detection(self):
        pass

    def test_not_loggedin_homepage_detection(self):
        pass

    def test_homepage_loggedin_detecction(self):
        pass

    def test_battlefield_detection(self):
        pass

    def test_keep_detection(self):
        pagetype = self.get_type_from_path(
            pagepaths.Keep.SIXKEYSNOBROKEN_REPAIRING)

        self.assertEqual(
            pagetype,
            rocenums.RocPageType.KEEP
        )

    def test_building_skills_upgrade_detection(self):
        pass


class RocCooldownPageTest(unittest.TestCase):
    def __init__(self, methodName: str = ...) -> None:
        super().__init__(methodName)
    # TODO add tests


class RocImageCaptchaPageTest(unittest.TestCase):
    def __init__(self, methodName: str = ...) -> None:
        super().__init__(methodName)

    # TODO add tests
