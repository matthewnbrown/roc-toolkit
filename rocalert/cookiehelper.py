import pickle
import browser_cookie3 as bc3
from urllib.parse import urlparse


def save_cookies_to_path(requests_cookiejar, filepath):
    with open(filepath, 'wb') as f:
        pickle.dump(requests_cookiejar, f)


def load_cookies_from_path(filename):
    try:
        with open(filename, 'rb') as f:
            return pickle.load(f)
    except EOFError:
        print("Error loading cookies file. Is it empty?")


__browser_lookup = {
    'all': bc3.load,
    'chrome': bc3.chrome,
    'firefox': bc3.firefox,
    'opera': bc3.opera,
    'edge': bc3.edge,
    'chromium': bc3.chromium,
    'brave': bc3.brave,
    'vivaldi': bc3.vivaldi,
    'safari': bc3.safari
}


def load_cookies_from_browser(browser: str, websiteurl: str = None):
    browser = browser.lower()
    if websiteurl is not None:
        dom = urlparse(websiteurl).netloc
        dom = '.'.join(dom.split('.')[-2:])
    else:
        dom = None

    if browser in __browser_lookup:
        try:
            cj = __browser_lookup[browser](domain_name=dom)
        except bc3.BrowserCookieError as e:
            print(f'Error: {e.args[0]}\nExiting...')
            quit()
    else:
        print(f'Error: Browser {browser} not found, acceptable browsers:')
        for browse in __browser_lookup:
            print(f'{browse}, ', end='')
        print('\nExiting...')
        quit()

    return cj
