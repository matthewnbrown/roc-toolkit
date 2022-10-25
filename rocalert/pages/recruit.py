import rocalert.pages.genericpages as genpages
from bs4 import BeautifulSoup
from datetime import datetime


class RocRecruitPage(genpages.RocImageCaptchaPage):
    def __init__(self, page: BeautifulSoup) -> None:
        super().__init__(page)
        recruit_form = page.find(id='spm_reset_form')

        spmtext = recruit_form.find('div', {'class': 'td c'}).text
        self._spm = int(spmtext.split(':')[1].strip())

        if self._captcha_hash is None:
            self._get_oncooldown(recruit_form)
        else:
            self._nextcaptchatime = datetime.now()

    def _get_oncooldown(self, recruit_form: BeautifulSoup) -> None:
        no_refresh = recruit_form.find(id='spm_no_refresh')
        resettime = no_refresh.find(
                'span', {'class': 'countdown'}).get('data-timestamp')
        self._nextcaptchatime = self._timestamp_to_datetime(int(resettime))

    @property
    def soldiers_per_minute(self) -> int:
        return self._spm

    @property
    def next_captcha_time(self) -> datetime:
        return self._nextcaptchatime
