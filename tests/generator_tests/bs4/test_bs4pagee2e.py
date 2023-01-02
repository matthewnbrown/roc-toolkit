import unittest
import unittest.mock as mock
import datetime as dt

import rocalert.enums as rocenums
import rocalert.models.pages as pages
import tests.generator_tests.pagepaths as pagepaths
import rocalert.pagegenerators.bs4 as generators
import rocalert.logging.timestampgenerator as timestampgen
from .pagehelpers import get_text_from_file


class BS4PageGenTest(unittest.TestCase):
    def _get_generator(
            self,
            timegenerator: timestampgen.DateTimeGeneratorABC = None):

        if timegenerator is None:
            timegenerator = mock.Mock()
            timegenerator.get_current_time.return_value = dt.datetime.now()

        return generators.BeautifulSoupPageGenerator(
            parser='lxml',
            timegenerator=timegenerator
        )

    def _generate_with_datetime_now(self, pagepath):
        generator = self._get_generator()
        pagehtml = get_text_from_file(pagepath)
        return generator.generate(pagehtml)

    def test_recruit_page_has_recruit_proper_components(self):
        page: pages.RecruitPage = self._generate_with_datetime_now(
            pagepaths.Recruit.HAS_CAPTCHA)

        self.assertEqual(page.page_type, rocenums.RocPageType.RECRUIT)
        self.assertIsNotNone(page.recruit)

    def test_armory_page_has_armory_proper_components(self):
        page: pages.ArmoryPage = self._generate_with_datetime_now(
            pagepaths.Armory.BASIC)

        self.assertEqual(page.page_type, rocenums.RocPageType.ARMORY)
        self.assertIsNotNone(page.armory)

    def test_training_page_has_training_proper_components(self):
        page: pages.TrainingPage = self._generate_with_datetime_now(
            pagepaths.Training.ALL_MERCS)

        self.assertEqual(page.page_type, rocenums.RocPageType.TRAINING)
        self.assertIsNotNone(page.training)

    def test_base_page_has_base_proper_components(self):
        page: pages.BasePage = self._generate_with_datetime_now(
            pagepaths.Base.BASE_WITH_OFFICERS)

        self.assertEqual(page.page_type, rocenums.RocPageType.BASE)
        self.assertIsNotNone(page.base)

    def test_keep_page_has_keep_proper_components(self):
        page: pages.KeepPage = self._generate_with_datetime_now(
            pagepaths.Keep.SIXKEYSNOBROKEN_REPAIRING)

        self.assertEqual(page.page_type, rocenums.RocPageType.KEEP)
        self.assertIsNotNone(page.keep)
