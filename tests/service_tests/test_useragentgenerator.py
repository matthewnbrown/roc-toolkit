import unittest
from unittest.mock import patch, MagicMock

from rocalert.services.useragentgenerator import UserAgentGenerator, Browser, OperatingSystem


@patch('rocalert.services.useragentgenerator.get_latest_user_agents')
class RocBuyerTests(unittest.TestCase):
    def __init__(self, methodName: str = ...) -> None:
        super().__init__(methodName)

    def test_when_no_latest_useragent_should_use_default(self, get_latest_agents: MagicMock):
        get_latest_agents.return_value = []

        defaultagent = 'somedefaultagent'

        sut = UserAgentGenerator(default=defaultagent)

        result = sut.get_useragent(
            browser=Browser.Chrome, operatingsystem=OperatingSystem.Windows)

        self.assertEqual(defaultagent, result)

    def test_when_no_latest_useragent_matchfilters_should_use_default(self, get_latest_agents: MagicMock):
        get_latest_agents.return_value = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/115.0']

        defaultagent = 'somedefaultagent'

        sut = UserAgentGenerator(default=defaultagent)

        result = sut.get_useragent(
            browser=Browser.Chrome, operatingsystem=OperatingSystem.Windows)

        self.assertEqual(defaultagent, result)
