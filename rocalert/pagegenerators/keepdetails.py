from bs4 import BeautifulSoup

from .generatortools import timestamp_to_datetime
import rocalert.models.pages.keep as rockeep


class KeepStatusGenerator:
    @classmethod
    def generate(cls, soup: BeautifulSoup) -> rockeep.KeepDetails:
        content = soup.find(id='content')
        keystatusarea = content.contents[5]
        keyspan = keystatusarea.find('span')

        keycounts = keyspan.find_all('b')
        keytypes = keyspan.find_all('small')

        keycount = 0
        brokenkeycount = 0

        for i in range(len(keycounts)):
            count = int(keycounts[i].text)
            keytype = keytypes[i].text

            if 'broken' in keytype:
                brokenkeycount += count
            else:
                keycount += count

        cd = content.find('span', {'class': 'countdown'})
        if cd:
            fintimestr = int(cd.get('data-timestamp'))
            repfinishtime = timestamp_to_datetime(fintimestr)
        else:
            repfinishtime = None

        return rockeep.KeepDetails(
            repairing=repfinishtime is not None,
            finish_repair_time=repfinishtime,
            key_count=keycount,
            broken_key_count=brokenkeycount
        )
