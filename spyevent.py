from collections import deque
from functools import partial
from tkinter import Entry, Canvas, Button, Frame, PhotoImage, Tk, NW
import cv2
import numpy as np
import tkinter
from typing import Callable, Iterable, List
from PIL import Image, ImageTk

from rocalert.roc_settings.settingstools import SettingsFileMaker, \
    SiteSettings, UserSettings
from rocalert.roc_web_handler import Captcha, RocWebHandler
from rocalert.services.manualcaptchaservice import ManualCaptchaService
from rocalert.cookiehelper import load_cookies_from_path, \
    load_cookies_from_browser
from os.path import exists

from rocalert.services.rocwebservices import BattlefieldPageService

# Comma separated ids
skip_ids = {1,2,3}

cookie_filename = 'cookies'


def __load_browser_cookies(roc: RocWebHandler, us: UserSettings) -> bool:
    if us.get_setting('load_cookies_from_browser'):
        cookies = load_cookies_from_browser(
            us.get_setting('browser'),
            roc.site_settings['roc_home']
            )
        roc.add_cookies(cookies)
        return True
    return False


def __load_cookies_file(roc: RocWebHandler, cookie_filename: str) -> bool:
    if exists(cookie_filename):
        print("Loading saved cookies")
        cookies = load_cookies_from_path(cookie_filename)
        if cookies is not None:
            roc.add_cookies(cookies)


def __log(s: str):
    print(s)


def login(roc: RocWebHandler, us: UserSettings):
    __log('Logging in.')
    if __load_browser_cookies(roc, us) and roc.is_logged_in():
        __log('Successfully pulled cookie from {}'.format(
            us.get_setting('browser')))
        return True

    if __load_cookies_file(roc, cookie_filename) and roc.is_logged_in():
        __log('Successfully used cookie file')
        return True

    roc.login(
        us.get_setting('email'),
        us.get_setting('password')
    )

    if roc.is_logged_in():
        __log("Login success.")
    else:
        __log("Login failure.")
        return False


def spyuser(roc: RocWebHandler, userid: str) -> bool:
    targeturl = roc.site_settings['roc_home'] \
        + f'/attack.php?id={userid}&mission_type=recon'
    captcha = roc.get_url_img_captcha(targeturl)
    if captcha is None:
        return False

    captchares = ManualCaptchaService().run_service(
        roc, None, {'captcha': captcha})

    validans = {str(i) for i in range(1, 10)}
    if 'error' in captchares or captchares['captcha'].ans not in validans:
        return False

    payload = {
        'defender_id': userid,
        'mission_type': 'recon',
        'reconspies': 1
    }

    return roc.submit_captcha_url(captcha, targeturl, payload, 'roc_spy')


def hit_spy_limit(responsetext: str) -> bool:
    return 'You cannot recon this person' in responsetext


def spyevent(
    rochandler: RocWebHandler,
    user_settings: UserSettings,
        ) -> None:

    if not login(rochandler, user_settings):
        print('Error logging in.')
        quit()

    i = 1
    while True:
        userlist = BattlefieldPageService.run_service(rochandler, i)
        i += 1
        if userlist['response'] == 'error':
            print('Finished.')
            break

        for user in userlist['result']:
            print(f'Current target: {user.name}')
            if int(user.id) in skip_ids:
                print('Skipping user')
                continue

            for j in range(10):
                valid_captcha = spyuser(rochandler, user.id)
                if not valid_captcha:
                    j -= 1
                if hit_spy_limit(rochandler.r.text):
                    print(f'Hit spy limit for {user.name}')
                    break


def runevent():
    user_settings_fp = 'user.settings'
    site_settings_fp = 'site.settings'
    buyer_settings_fp = 'buyer.settings'

    if SettingsFileMaker.needs_user_setup(
            user_settings_fp, site_settings_fp, buyer_settings_fp):
        print("Exiting. Please fill out settings files")
        quit()

    user_settings = UserSettings(filepath=user_settings_fp)
    site_settings = SiteSettings(filepath=site_settings_fp)
    rochandler = RocWebHandler(site_settings)

    spyevent(rochandler, user_settings)


def _bytesimage_to_photoimage_resize(
        image,
        newx: int = 150,
        newy: int = 150
        ) -> PhotoImage:
    nparr = np.asarray(image, dtype=np.uint8)
    img_np = cv2.imdecode(nparr, cv2.IMREAD_GRAYSCALE)
    img_np_resize = cv2.resize(
                    img_np, (newx, newy), fx=0, fy=0,
                    interpolation=cv2.INTER_CUBIC)
    photoimage = ImageTk.PhotoImage(image=Image.fromarray(img_np_resize))
    return photoimage


class MulticaptchaGUI:
    def __init__(
            self,
            captchas: List[Captcha],
            on_selection: Callable,
            getnewcaptchas: Callable,
            captcha_xcount: int = 4,
            captcha_ycount: int = 1
            ) -> None:
        """_summary_

        Args:
            captchas (List[Captcha]): _description_
                List of inital set of captchas
            on_selection (Callable): _description_
                Callback function that will be passed the solved captchas
            getnewcaptchas (Callable): _description_
                Callback function that should return a list of captchas
            captcha_xcount (int, optional): _description_. Defaults to 4.
            captcha_ycount (int, optional): _description_. Defaults to 1.
        """
        self._root = Tk()
        self._root.call('wm', 'attributes', '.', '-topmost', '1')

        self._captchas = deque(captchas)
        images = self._create_imgs_from_captchas(captchas)
        self._images = deque(images)

        self._xcaptchacount = captcha_xcount
        self._ycaptchacount = captcha_ycount

        self._onselect = on_selection
        self._getcaptchas = getnewcaptchas

        self.entry = Entry(self._root)
        self.user_num_selection = '0'

        self._root.bind("<Key>", self.__on_keypress)

        self._canvasframe = Frame(self._root)
        self._canvases = [Canvas(self._canvasframe,
                                 height=150,
                                 width=150)
                          for i in range(self._captchawindowscount)]

        for y in range(captcha_ycount):
            for x in range(captcha_xcount):
                self._canvases[x + y * captcha_xcount].grid(row=y, column=x)

        self._canvasframe.grid(row=0, column=0)

        frame = Frame(self._root)
        frame.grid(row=captcha_ycount, column=0)

        self._add_buttons(frame)
        self._update_captcha_view()

    @classmethod
    def _create_imgs_from_captchas(cls,
                                   captchas: Iterable[Captcha]
                                   ) -> List[Captcha]:
        res = []
        for captcha in captchas:
            res.append(_bytesimage_to_photoimage_resize(captcha.img))

        return res

    @property
    def _captchawindowscount(self) -> int:
        return self._xcaptchacount * self._ycaptchacount

    def _update_captcha_view(self) -> None:
        for i in range(min(len(self._captchas), self._captchawindowscount)):
            self._canvases[i].delete('all')
            self._canvases[i].create_image(0, 0,
                                           anchor=NW,
                                           image=self._images[i])

        for i in range(self._captchawindowscount - len(self._captchas)):
            self._canvases[self._captchawindowscount - i-1].delete('all')

    def _add_new_captchas(self) -> None:
        newcaptachas = self._getcaptchas()
        newimgs = self._create_imgs_from_captchas(newcaptachas)
        self._captchas.extend(newcaptachas)
        self._images.extend(newimgs)

        while len(newcaptachas) > 0 and \
                len(self._captchas) < self._captchawindowscount:
            newcaptachas = self._getcaptchas()
            self._captchas.extend(newcaptachas)

        self._update_captcha_view()

    def __on_keypress(self, event: tkinter.EventType.KeyPress):
        key = event.keysym
        if key.isnumeric() and int(key) > 0:
            self._answer_selected(key)

    def __on_button_click(self, num_str):
        self._answer_selected(num_str)

    def _add_buttons(self, root):
        rows = 3
        cols = 3
        for i in range(rows):
            for j in range(cols):
                num = str(i*(rows) + j+1)
                action_with_arg = partial(self.__on_button_click, num)
                but = Button(root, text=num, command=action_with_arg)
                but.grid(row=i, column=j)

    def _check_finished(self) -> None:
        if len(self._captchas) == 0:
            self._end_event()

    def _answer_selected(self, answer: str) -> None:
        self._images.popleft()
        cap = self._captchas.popleft()

        cap.ans = answer
        self._onselect(cap)
        self._add_new_captchas()

        self._check_finished()

    def _end_event(self) -> None:
        self._root.destroy()

    def start_event(self) -> None:
        self._root.mainloop()


def test_multiimage(
        path: str,
        getnewcaptcha: Callable = None,
        oncaptchasolve: Callable = None
        ) -> None:

    import glob
    imagelist = []

    for filename in glob.glob(path+'/*.png'):
        # im = Image.open(filename)
        with open(filename, 'rb') as image:
            f = image.read()
            b = bytearray(f)
            imagelist.append((filename, b))

    def getcapchtas():
        if len(imagelist) == 0:
            return []
        filename, image = imagelist.pop()
        cap = Captcha(filename, image, captype='img')
        return [cap]

    def oncaptchasolve(ans: str):
        print(f'captcha solved with ans {ans}')
    x, y = 6, 1

    startcap = []

    for i in range(x*y):
        startcap += getcapchtas()

    event = MulticaptchaGUI(startcap, oncaptchasolve, getcapchtas, x, y)

    event.start_event()


test_multiimage('D:/')
#runevent()
