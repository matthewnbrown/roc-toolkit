from dataclasses import dataclass
from typing import Tuple
import rocalert.pages.genericpages as genpages
from bs4 import BeautifulSoup
import datetime


@dataclass(frozen=True)
class RocEvent:
    name: str
    description: str
    date: datetime
    is_active: bool


@dataclass(frozen=True)
class RocActivity:
    date: datetime
    activity_text: str


class RocBasePage(genpages.RocUserPage):
    def __init__(self, page: BeautifulSoup) -> None:
        super().__init__(page)

        base_container = page.find(id='base_container')

        self._get_base_details(base_container)
        self._get_events(base_container)
        self._get_personal_totals_table(base_container)
        self._get_recent_activity(base_container)
        self._get_soldier_source_table(base_container)

        wtsoup = base_container.find(id='weaponsandtroops_panel').find('table')
        self._weapondisttable = genpages.WeaponTroopDistTable(wtsoup)
        stsoup = base_container.find(
            id='militaryeffectiveness_panel').find('table')
        self._stattable = genpages.StatTable(stsoup)

    def _get_base_details(self, base_container: BeautifulSoup) -> None:
        pass

    def _get_events(self, base_container: BeautifulSoup) -> None:
        eventlist = base_container.find(id='events')
        listitems = eventlist.findChildren(
            'li', {'class', 'td'}, recursive=False)
        self._events = []

        def is_event(eventsoup: BeautifulSoup) -> bool:
            isevent = eventsoup.find('span', {'class': 'countdown'})
            return isevent is not None

        def is_current(eventsoup: BeautifulSoup) -> bool:
            return 'ends in' in eventsoup.text

        def get_name(eventsoup: BeautifulSoup) -> str:
            return eventsoup.find('b').text

        def get_desc(eventsoup: BeautifulSoup) -> str:
            return eventsoup.find('small').text

        def get_date(eventsoup: BeautifulSoup) -> datetime:
            cdspan = eventsoup.find('span', {'class': 'countdown'})
            timestamp = cdspan.get('data-timestamp')
            return self._timestamp_to_datetime(int(timestamp))

        for event in listitems:
            if not is_event(event):
                continue

            self._events.append(
                RocEvent(
                    get_name(event), get_desc(event),
                    get_date(event), is_current(event))
            )

    def _get_soldier_source_table(self, base_container: BeautifulSoup) -> None:
        pass

    def _get_recent_activity(self, base_container: BeautifulSoup) -> None:
        self._recent_activity = []
        alog = base_container.find(id='activitylog_panel')
        acts = alog.findChildren('div', {'class': 'info_container'})

        for act in acts:
            children = act.findChildren(recursive=False)
            timestamp = children[0].find('span').get('data-timestamp')
            act_date = self._timestamp_to_datetime(int(timestamp))
            act_text = children[1].text
            self._recent_activity.append(RocActivity(act_date, act_text))

    def _get_personal_totals_table(
            self, base_container: BeautifulSoup) -> None:
        pass

    def _get_officers(self, base_container: BeautifulSoup) -> None:
        pass

    @property
    def alliance(self) -> Tuple[str, str]:
        """_summary_

        Returns:
            Tuple[str, str]: _description_
            Tuple of alliance name and link to alliance page
        """
        return self._alliance

    @property
    def commander(self) -> Tuple[str, str]:
        """_summary_

        Returns:
            Tuple[str, str]: _description_
            Tuple of commander name and link to their page
        """
        return self._commander

    @property
    def officers(self) -> list[Tuple[str, str]]:
        return self._officers

    @property
    def current_events(self) -> list[RocEvent]:
        return [event for event in self._events if event.is_active]

    @property
    def upcoming_events(self) -> list[RocEvent]:
        return [event for event in self._events if not event.is_active]

    @property
    def events(self) -> list[RocEvent]:
        return self._events

    @property
    def recenty_activity(self) -> list[RocActivity]:
        return self._recent_activity

    @property
    def server_datetime(self) -> str:
        return self._serverdatetime

    @property
    def personal_totals_table(self):
        # TODO: Type this properly
        return self._personaltotals

    @property
    def soldier_source_table(self):
        # TODO: Type this properly
        return self._soldiersources

    @property
    def keys_found(self) -> int:
        return self._keysfound

    @property
    def loot_found(self) -> int:
        return self._lootfound

    @property
    def last_active(self) -> datetime:
        return self._lastactive

    @property
    def best_rank(self) -> Tuple[int, datetime.datetime]:
        return self._bestrank

    @property
    def army(self) -> str:
        return self._army

    @property
    def race_bonuses(self) -> list[str]:
        return self._racebonuses

    @property
    def turn_based_gold(self) -> int:
        return self._tbg

    @property
    def weapon_distribution_table(self) -> genpages.WeaponTroopDistTable:
        return self._weapondisttable

    @property
    def stats_table(self) -> genpages.StatTable:
        return self._stattable
