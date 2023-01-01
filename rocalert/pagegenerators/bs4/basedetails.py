from bs4 import BeautifulSoup
from typing import Tuple
import datetime as dt

from .generatortools import timestamp_to_datetime
import rocalert.models.pages.base as rocbase


# TODO: FINISH IMPLEMENTING THIS
class BaseDetailsGenerator:
    @classmethod
    def generate(cls, soup: BeautifulSoup) -> rocbase.BaseDetails:
        base_container = soup.find(id='base_container')

        basedetails = rocbase.BaseDetails()
        cls._get_base_details(base_container, basedetails)
        cls._get_events(base_container, basedetails)
        cls._get_recent_activity(base_container, basedetails)
        cls._get_soldier_source_table(base_container, basedetails)
        cls._get_personal_totals_table(base_container, basedetails)
        return basedetails

    @classmethod
    def _get_base_details(
            cls,
            base_container: BeautifulSoup,
            basedetails: dict) -> None:
        pass

    @classmethod
    def _get_events(
            cls,
            base_container: BeautifulSoup,
            basedetails: rocbase.BaseDetails) -> None:
        eventlist = base_container.find(id='events')
        listitems = eventlist.findChildren(
            'li', {'class', 'td'}, recursive=False)
        current_events = []
        upcoming_events = []

        def is_event(eventsoup: BeautifulSoup) -> bool:
            isevent = eventsoup.find('span', {'class': 'countdown'})
            return isevent is not None

        def is_current(eventsoup: BeautifulSoup) -> bool:
            return 'ends in' in eventsoup.text

        def get_name(eventsoup: BeautifulSoup) -> str:
            return eventsoup.find('b').text

        def get_desc(eventsoup: BeautifulSoup) -> str:
            return eventsoup.find('small').text

        def get_date(eventsoup: BeautifulSoup) -> dt.datetime:
            cdspan = eventsoup.find('span', {'class': 'countdown'})
            timestamp = cdspan.get('data-timestamp')
            return timestamp_to_datetime(int(timestamp))

        for event in listitems:
            if not is_event(event):
                continue

            rocevent = rocbase.RocEvent(
                    get_name(event), get_desc(event),
                    get_date(event), is_current(event))

            if is_current(event):
                current_events.append(rocevent)
            else:
                upcoming_events.append(rocevent)

        basedetails.current_events = current_events
        basedetails.upcoming_events = upcoming_events

    @classmethod
    def _get_soldier_source_table(
            cls,
            base_container: BeautifulSoup,
            basedetails: rocbase.BaseDetails) -> None:
        pass

    @classmethod
    def _get_recent_activity(
            cls, base_container: BeautifulSoup,
            basedetails: rocbase.BaseDetails
            ) -> None:
        recent_activity = []
        alog = base_container.find(id='activitylog_panel')
        acts = alog.findChildren('div', {'class': 'info_container'})

        for act in acts:
            children = act.findChildren(recursive=False)
            timestamp = children[0].find('span').get('data-timestamp')
            act_date = timestamp_to_datetime(int(timestamp))
            act_text = children[1].text
            recent_activity.append(rocbase.RocActivity(act_date, act_text))

        basedetails.recent_activity = recent_activity

    @classmethod
    def _get_personal_totals_table(
            cls, base_container: BeautifulSoup,
            basedetails: rocbase.BaseDetails
            ) -> None:
        pass

    @classmethod
    def _get_officers(
            cls, base_container: BeautifulSoup,
            basedetails: rocbase.BaseDetails
            ) -> list[Tuple[str, str]]:
        pass
