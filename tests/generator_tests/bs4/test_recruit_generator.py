import unittest

from .pagehelpers import getsoup
import rocalert.models.pages.recruit as rocrecruit
import rocalert.pagegenerators.bs4 as generators
import tests.generator_tests.pagepaths as pagepaths


class RecruitDetailGeneratorTest(unittest.TestCase):
    def _get_no_captcha_pagedetails(self) -> rocrecruit.RecruitDetails:
        path = pagepaths.Recruit.NOCAPTCHA
        soup = getsoup(path)
        return generators.RecruitDetailsGenerator.generate(soup)

    def _get_captcha_pagedetails(self) -> rocrecruit.RecruitDetails:
        path = pagepaths.Recruit.HAS_CAPTCHA
        soup = getsoup(path)
        return generators.RecruitDetailsGenerator.generate(soup)

    def test_nocaptcha_captcha_status(self):
        details = self._get_no_captcha_pagedetails()
        self.assertFalse(details.requires_captcha)

    def test_nocaptcha_spm(self):
        details = self._get_no_captcha_pagedetails()
        spm = details.soldiers_per_minute
        self.assertEqual(
            spm,
            70,
            'Soldiers per minute is not correct value'
        )

    def test_captcha_spm(self):
        details = self._get_captcha_pagedetails()
        spm = details.soldiers_per_minute

        self.assertEqual(
            spm,
            60,
            'Soldiers per minute is not correct value'
        )
