from bs4 import BeautifulSoup

from .generatortools import timestamp_to_datetime
import rocalert.models.pages.recruit as rocrecruit


# TODO: FINISH THIS
class RecruitDetailsGenerator:
    @classmethod
    def generate(cls, soup: BeautifulSoup) -> rocrecruit.RecruitDetails:
        recruit_form = soup.find(id='spm_reset_form')

        spmtext = recruit_form.find('div', {'class': 'td c'}).text
        spm = int(spmtext.split(':')[1].strip())

        captchaimg = recruit_form.find(id='captcha_image')
        if captchaimg is None:
            cd = cls._get_oncooldown(recruit_form)
        else:
            cd = None

        return rocrecruit.RecruitDetails(
            soldiers_per_minute=spm,
            next_captcha_time=cd,
            requires_captcha=cd is None
        )

    @classmethod
    def _get_oncooldown(cls, recruit_form: BeautifulSoup) -> None:
        no_refresh = recruit_form.find(id='spm_no_refresh')
        resettime = no_refresh.find(
                'span', {'class': 'countdown'}).get('data-timestamp')
        return timestamp_to_datetime(int(resettime))
