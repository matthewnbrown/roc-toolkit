from cookiehelper import *
from pyroccaptchaselector import *
from pyrocaltertgui import get_user_answer_captcha
import time
import random
from tkinter import *
import requests # py -m pip install requests
from os.path import exists

username = "email@email.com"
password = "password123"
notify_soldier_amt = 60
min_checktime_secs = 5*60
max_checktime_secs = 10*60


roc_home = "enter_home"
roc_login = "enter_login"
roc_recruit = "enter_recruit"

cookie_filename = 'cookies'
headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}

s = requests.Session()

def go_to_page(url) -> requests.Response:
    return s.get(url, headers=headers)

def is_logged_in(resp = None) -> bool:
    if resp is None:
        resp = go_to_page(roc_home)
    return r'email@address.com' not in resp.text

def login() -> bool:
    payload = {
        'email':username,
        'password':password
    }
    p = s.post(roc_login, payload)
    return r'Incorrect login' not in p.text

def check_captcha(r) -> bool:
    return '[click the correct number to proceed]' in r.text

def get_captcha_image(resp):
    index = resp.text.find('img.php?hash=')
    imgurl = resp.text[index:resp.text.find('"', index, index+100)]

    img = go_to_page(roc_home + imgurl).content
    #with open('image_name.png', 'wb') as handler:
    #    handler.write(img)
    return img


def send_captcha_ans(ans):
    cs = ROCCaptchaSelector()
    ans_coords = cs.get_xy_static(ans)
    print(ans, ans_coords)
    pass

if __name__== '__main__':
    if exists(cookie_filename):
        print("Loading saved cookies")
        cookies = load_cookies(cookie_filename)
        s.cookies.update(cookies)

    consecutive_login_failures = 0

    while True:
        if consecutive_login_failures == 2:
            print("ERROR: Multiple login failures. Exiting.")
            break

        r = go_to_page(roc_recruit)

        if not is_logged_in(r):
            print("Session timed out. Logging back in: ", end = "")
            res = login()
            if res:
                consecutive_login_failures = 0
                print("Login success")
            else:
                consecutive_login_failures += 1
                print("login failure")
            time.sleep(2)
            continue

        if check_captcha(r):
            img = get_captcha_image(r)
            ans = get_user_answer_captcha(img)
            print("Captcha!", ans)
        else:
            print("No captcha")
        
        waitTime = min_checktime_secs + int(random.uniform(0,1) * max_checktime_secs)
        save_cookies(s.cookies, cookie_filename)
        print(f'Taking a nap. Talk to you in {waitTime} seconds')
        time.sleep(waitTime);