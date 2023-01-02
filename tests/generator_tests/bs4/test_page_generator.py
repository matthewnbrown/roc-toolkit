import unittest

from .pagehelpers import getsoup
import rocalert.models.pages.genericpages as gp
import rocalert.pagegenerators.bs4 as generators
import rocalert.enums as rocenums
import tests.generator_tests.pagepaths as pagepaths

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

    # TODO
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
