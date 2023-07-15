from enum import Enum, auto
from latest_user_agents import get_latest_user_agents


class Browser(Enum):
    Chrome = auto()
    Firefox = auto()
    Safari = auto()
    Any = auto()


_browsermap = {
    Browser.Chrome: "Chrome",
    Browser.Firefox: "Firefox",
    Browser.Safari: "Safari",
    Browser.Any: ""
}


class OperatingSystem(Enum):
    Windows = auto()
    Mac = auto()
    Fedora = auto()
    Linux64 = auto()
    Ubuntu = auto()
    Any = auto()


_osmap = {
    OperatingSystem.Windows: "Windows NT 10.0; Win64; x64",
    OperatingSystem.Mac: "Macintosh",
    OperatingSystem.Fedora: "Fedora",
    OperatingSystem.Linux64: "Linux x86_64)",
    OperatingSystem.Ubuntu: "Ubuntu",
    OperatingSystem.Any: ""
}


def _browser_filter(browser: Browser, value: str) -> bool:
    if browser not in _browsermap:
        raise ValueError(f'Browser not of known type: {browser}')

    return _browsermap[browser] in value


def _os_filter(os: OperatingSystem, value: str) -> bool:
    if os not in _osmap:
        raise ValueError()

    return _osmap[os] in value


class UserAgentGenerator:
    def __init__(self, default: str = None) -> None:
        default_useragent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) ' \
            + 'AppleWebKit/537.36 (KHTML, like Gecko) ' \
            + 'Chrome/114.0.0.0 Safari/537.36'
        self._default = default_useragent if default is None else default

    def get_useragent(self, browser: Browser, operatingsystem: OperatingSystem) -> str:
        latest_agents = self._get_latest_agents()

        browser_agents = list(filter(
            lambda x: _browser_filter(browser, x), latest_agents))
        filtered_agents = list(filter(lambda x: _os_filter(
            operatingsystem, x), browser_agents))

        if len(filtered_agents) == 0:
            return self._default

        return filtered_agents[0]

    @staticmethod
    def _get_latest_agents() -> list[str] | None:
        try:
            latest_agents = get_latest_user_agents()
            if latest_agents is None or type(latest_agents) != list:
                return []
        except Exception as e:
            print('An error occurent when looking up useragents: ' + e)
            return []

        return latest_agents
