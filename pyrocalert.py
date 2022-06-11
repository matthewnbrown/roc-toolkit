from cookiehelper import *
from pyroccaptchaselector import *
from pyrocaltertgui import get_user_answer_captcha
import roc_auto_solve
from settingstools import UserSettings, SiteSettings

import io
import PIL.Image
import time
import datetime
import random
import requests # py -m pip install requests
from os.path import exists

cookie_filename = 'cookies'
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.63 Safari/537.36'}
user_settings =  UserSettings(filepath='user.settings')
user_settings = user_settings.get_settings()
site_settings = SiteSettings(filepath='site.settings')
site_settings = site_settings.get_settings()

validans = { str(i) for i in range(1,10) }
s = requests.Session()

def go_to_page(url) -> requests.Response:
    return s.get(url, headers=headers)

def is_logged_in(resp = None) -> bool:
    if resp is None:
        resp = go_to_page(site_settings['roc_home'])
    return r'email@address.com' not in resp.text

def login() -> bool:
    payload = {
        'email':user_settings['email'],
        'password':user_settings['password']
    }
    p = s.post(site_settings['roc_login'], payload)
    return r'Incorrect login' not in p.text

def check_captcha(r) -> bool:
    return '[click the correct number to proceed]' in r.text

def get_imagehash_from_resp(resp) -> str:
    index = resp.text.find('img.php?hash=')
    imghash = resp.text[index + len('img.php?hash='):resp.text.find('"', index, index+100)]
    return imghash

def get_captcha_image(hash):
    imgurl = 'img.php?hash=' + hash
    img = go_to_page(site_settings['roc_home'] + imgurl).content
    #with open('image_name.png', 'wb') as handler:
    #    handler.write(img)
    return img

def send_captcha_ans(hash, ans) -> bool:
    cs = ROCCaptchaSelector()
    ans_coords = cs.get_xy_static(ans)
    print(ans, ans_coords)

    payload = {
        'captcha':hash,
        'coordinates[x]':ans_coords[0],
        'coordinates[y]':ans_coords[1],
        'num':ans,
    }
    p = s.post(site_settings['roc_recruit'], payload)
    return not check_captcha(p)

def get_captcha_ans(img, hash) -> str:
    path = save_captcha(img, hash)

    if user_settings['auto_solve_captchas']:
        return roc_auto_solve.Solve(user_settings['auto_captcha_key'], path)
    else:
        return get_user_answer_captcha(img)

def save_captcha(img_bytes, hash):
    img = PIL.Image.open(io.BytesIO(img_bytes))
    path = user_settings['captcha_save_path'] + hash + '.png'
    img.save(path)
    return path;

def in_nightmode() -> bool:
    if not user_settings['enable_nightmode']:
        return False
    start, end = user_settings['nightmode_begin'], user_settings['nightmode_end']
    now = datetime.datetime.now().time()

    if start <= end :
        return start <= now <= end
    else:
        return start <= now or now <= end

def get_waittime() -> int:
    if not in_nightmode():
        min = user_settings['min_checktime_secs']
        max = user_settings['max_checktime_secs']
    else:
        min = user_settings['nightmode_minwait_mins'] * 60
        max = user_settings['nightmode_maxwait_mins'] * 60
    return min + int(random.uniform(0,1) * max)
 
if __name__== '__main__':
    if exists(cookie_filename):
        print("Loading saved cookies")
        cookies = load_cookies(cookie_filename)
        s.cookies.update(cookies)

    consecutive_login_failures = 0
    consecutive_captcha_failures = 0
    consecutive_answer_errors = 0
    while True:
        if consecutive_login_failures == 2:
            print("ERROR: Multiple login failures. Exiting.")
            break

        r = go_to_page(site_settings['roc_recruit'])

        if not is_logged_in(r):
            print("Session timed out. Logging back in: ", end = "")
            res = login()
            if res:
                consecutive_login_failures = 0
                print("Login success")
                save_cookies(s.cookies, cookie_filename)
            else:
                consecutive_login_failures += 1
                print("Login failure")
            time.sleep(2)
            continue

        if check_captcha(r):
            print('Detected captcha...')
            hash = get_imagehash_from_resp(r)
            img = get_captcha_image(hash)
            ans = get_captcha_ans(img, hash)
            if len(ans) != 1 or ans not in validans:
                print("Warning: received response \'{}\' from captcha solver!".format(ans))
                consecutive_answer_errors += 1
                if consecutive_answer_errors > 2:
                    print("Too many consecutive bad answers received, exiting!")
                    break
                continue
           
            consecutive_answer_errors = 0
                    
            correct = send_captcha_ans(hash, ans)
            if correct:
                print("Correct answer")
                consecutive_captcha_failures = 0
            else:
                print("Incorrect answer")
                consecutive_captcha_failures += 1
                if consecutive_captcha_failures > 3:
                    print("Failed too many captchas, exiting!")
                    break
                continue
            
        else:
            print("No captcha needed")
        
        waitTime = get_waittime()
        save_cookies(s.cookies, cookie_filename)
        endtime = datetime.datetime.now() + datetime.timedelta(0, waitTime)
        print('Taking a nap. Waking up at {}.'.format(endtime.strftime('%H:%M:%S')))
        time.sleep(waitTime)