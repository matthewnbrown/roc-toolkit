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

    def test_browsers_match_correctly(self, get_latest_agents: MagicMock):
        browser_expected_map = {
            Browser.Firefox: 'Mozilla/5.0 (Linux x86_64; rv:85.0) Gecko/20100101 Firefox/85.0',
            Browser.Chrome: 'Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.182 Safari/537.36',
            Browser.Edge: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.182 Safari/537.36 Edg/88.0.705.68'
        }

        for browser, expected in browser_expected_map.items():
            with self.subTest(browser=browser):
                get_latest_agents.return_value = [
                    'Mozilla/5.0 (Linux x86_64; rv:85.0) Gecko/20100101 Firefox/85.0',
                    'Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.182 Safari/537.36',
                    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.182 Safari/537.36 Edg/88.0.705.68']

                sut = UserAgentGenerator(default="someval")
                result = sut.get_useragent(
                    browser=browser, operatingsystem=OperatingSystem.Any)
                self.assertEqual(expected, result)

    def test_operatingsystem_match_correctly(self, get_latest_agents: MagicMock):
        os_expected_map = {
            OperatingSystem.Windows: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.182 Safari/537.36',
            OperatingSystem.Fedora: 'Mozilla/5.0 (X11; Fedora; Linux x86_64; rv:78.0) Gecko/20100101 Firefox/78.0',
            OperatingSystem.Linux64: 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.182 Safari/537.36',
            OperatingSystem.Mac: 'Mozilla/5.0 (Macintosh; Intel Mac OS X 11.2; rv:78.0) Gecko/20100101 Firefox/78.0',
            OperatingSystem.Ubuntu: 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:85.0) Gecko/20100101 Firefox/85.0'
        }

        for os, expected in os_expected_map.items():
            with self.subTest(operatingsystem=os):
                get_latest_agents.return_value = [
                    'Mozilla/5.0 (Macintosh; Intel Mac OS X 11.2; rv:78.0) Gecko/20100101 Firefox/78.0',
                    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.182 Safari/537.36',
                    'Mozilla/5.0 (X11; Fedora; Linux x86_64; rv:78.0) Gecko/20100101 Firefox/78.0',
                    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.182 Safari/537.36',
                    'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:85.0) Gecko/20100101 Firefox/85.0'
                ]

                sut = UserAgentGenerator(default="someval")
                result = sut.get_useragent(
                    browser=Browser.Any, operatingsystem=os)
                self.assertEqual(expected, result)

    def test_operating_and_browser_match_correctly(self, get_latest_agents: MagicMock):
        os_expected_map = [
            (Browser.Chrome, OperatingSystem.Windows,
             'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.182 Safari/537.36'),
            (Browser.Safari, OperatingSystem.Mac,
             'Mozilla/5.0 (Macintosh; Intel Mac OS X 13_4_1) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.5 Safari/605.1.15'),
            (Browser.Firefox, OperatingSystem.Ubuntu,
             'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:85.0) Gecko/20100101 Firefox/85.0')
        ]

        for browser, os, expected in os_expected_map:
            with self.subTest(operatingsystem=os, browser=browser):
                get_latest_agents.return_value = [
                    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.182 Safari/537.36',
                    'Mozilla/5.0 (Macintosh; Intel Mac OS X 13_4_1) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.5 Safari/605.1.15',
                    'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:85.0) Gecko/20100101 Firefox/85.0'
                ]

                sut = UserAgentGenerator(default="someval")
                result = sut.get_useragent(
                    browser=browser, operatingsystem=os)
                self.assertEqual(expected, result)
