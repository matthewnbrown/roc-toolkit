import pickle
import browser_cookie3
from urllib.parse import urlparse
 # py -m pip install browser-cookie3

def save_cookies_to_path(requests_cookiejar, filepath):
    with open(filepath, 'wb') as f:
        pickle.dump(requests_cookiejar, f)

def load_cookies_from_path(filename):
    with open(filename, 'rb') as f:
        return pickle.load(f)


def load_cookies_from_browser(browser: str, websiteurl: str = None):
    browser = browser.lower()
    if websiteurl is not None:
        dom = urlparse(websiteurl).netloc
        dom = '.'.join(dom.split('.')[-2:])
    else:
        dom = None
    if browser == 'firefox':
        cj = browser_cookie3.firefox(domain_name=dom)
    elif browser == 'chrome':
        cj= browser_cookie3.chrome()
    else:
        return None

    return cj


