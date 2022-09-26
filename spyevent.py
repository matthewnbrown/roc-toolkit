from collections import defaultdict, deque
from typing import Callable, Deque, Iterable, List, Set
from os.path import exists
from functools import partial
from threading import Thread, Lock
from tkinter import Entry, Canvas, Button, Frame, PhotoImage, Tk, NW, Event
from PIL import Image, ImageTk
import cv2
import numpy as np

from rocalert.roc_settings.settingstools import SettingsFileMaker, \
    SiteSettings, UserSettings
from rocalert.roc_web_handler import Captcha, RocWebHandler
from rocalert.rocaccount import BattlefieldTarget
from rocalert.cookiehelper import load_cookies_from_path, \
    load_cookies_from_browser, save_cookies_to_path
from rocalert.services.rocwebservices import BattlefieldPageService

# Comma separated ids. Put your own ID in here
skip_ids = {7530}

# This will only spy on selected IDs. Skip_ids will be ignored
onlyspy_ids = {}
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
        save_cookies_to_path(roc.get_cookies(), cookie_filename)
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
        save_cookies_to_path(roc.get_cookies(), cookie_filename)
        return True
    else:
        __log("Login failure.")
        return False


class SpyEvent:
    class SpyStatus:
        def __init__(self) -> None:
            self.active_captchas = 0
            self.solved_captchas = 0

        @property
        def required_captchas(self):
            return max(10 - self.solved_captchas - self.active_captchas, 0)

    def __init__(
            self,
            roc: RocWebHandler,
            skiplist: Set[str] = set(),
            onlyspylist: Set[str] = set()
            ) -> None:
        """_summary_

        Args:
            roc (RocWebHandler): _description_
                ROC session to use for spy event
            skiplist (Set[str], optional): _description_. Default: Set().
                List of user IDs to not spy
            onlyspylist (Set[str], optional): _description_. Default: Set().
                List of user IDs that will only be spied on.
                All other users will be skipped if this
                parameter is not None or an empty list
        """
        self._roc = roc
        self._skiplist = skiplist
        self._onlyspylist = onlyspylist
        self._restrictedtargets = onlyspylist and len(onlyspylist) > 0
        self._captchamap = {}
        self._usercaptchas = defaultdict(set)
        self._spystatus = defaultdict(self.SpyStatus)
        self._bflock = Lock()
        self._battlefield = None
        self._captchamaplock = Lock()
        self._updating_captchas = False

    def _hit_spy_limit(self, responsetext: str) -> bool:
        return 'You cannot recon this person' in responsetext

    def _get_captcha(self, user: BattlefieldTarget) -> Captcha:
        url = self._get_spy_url(user)
        captcha = self._roc.get_url_img_captcha(url)
        return captcha

    def _get_spy_url(self, user: BattlefieldTarget) -> str:
        return self._roc.site_settings['roc_home'] \
            + f'/attack.php?id={user.id}&mission_type=recon'

    def _userfilter(
            self,
            new_users: Iterable[BattlefieldTarget]
            ) -> Deque[BattlefieldTarget]:
        res = deque()
        if self._onlyspylist and len(self._onlyspylist) > 0:
            for user in new_users:
                if user.id in self._onlyspylist:
                    res.append(user)
            return res

        for user in new_users:
            if user.id not in self._skiplist:
                res.append(user)
        return res

    def _get_all_users(self) -> None:
        self._bflock.acquire()
        pagenum = 1
        self._battlefield = self._battlefield if self._battlefield else deque()

        while True:
            user_resp = BattlefieldPageService.run_service(self._roc, pagenum)
            pagenum += 1
            if user_resp['response'] == 'error':
                self._bflock.release()
                return

            newuser = self._userfilter(user_resp['result'])
            self._battlefield.extend(newuser)

    def _handle_maxed_target(self, user: BattlefieldTarget) -> None:
        print(f'Maxed out spy attempts on {user.name}')
        for captcha in self._usercaptchas[user]:
            del self._captchamap[captcha]

        self._spystatus[user].active_captchas = 0
        self._spystatus[user].solved_captchas = 10

        self._gui.remove_captchas(self._usercaptchas[user])
        del self._usercaptchas[user]

    def _getnewcaptchas(self, num_captchas: int) -> List[Captcha]:
        backup = []
        result = []
        self._bflock.acquire()
        while num_captchas > 0 and len(self._battlefield) > 0:
            cur_user = self._battlefield.popleft()
            backup.append(cur_user)
            count = self._spystatus[cur_user].required_captchas
            num_captchas -= count

            for i in range(count):
                cap = self._get_captcha(cur_user)

                if cap and cap.type == cap.CaptchaType.TEXT:
                    print("Warning: Received TEXT Captcha"
                          + ' attempting captcha reset')
                    self._roc.reset_cooldown()
                    i -= 1
                    continue

                if cap is None or cap.hash is None:
                    i -= 1
                    print(f'Failed getting captcha for {cur_user.name}')
                    continue

                self._captchamaplock.acquire()
                self._captchamap[cap] = cur_user
                self._usercaptchas[cur_user].add(cap)
                self._spystatus[cur_user].active_captchas += 1
                self._captchamaplock.release() 

                result.append(cap)

        while len(backup) > 0:
            self._battlefield.appendleft(backup.pop())
        self._bflock.release()
        return result

    def _send_captchas_to_gui(self, captchas: List[Captcha]) -> None:
        self._gui.add_captchas(captchas)

    def _getsend_captchas(self, count) -> None:
        self._captchamaplock.acquire()
        updating = self._updating_captchas

        if not updating:
            self._updating_captchas = True
        self._captchamaplock.release()

        if not updating:
            caps = self._getnewcaptchas(count)
            self._send_captchas_to_gui(caps)
            self._captchamaplock.acquire()
            self._updating_captchas = False
            self._captchamaplock.release()

    def _oncaptchasolved(self, captcha: Captcha) -> None:
        self._captchamaplock.acquire()
        user = self._captchamap[captcha]
        self._captchamaplock.release()

        targeturl = self._get_spy_url(user)

        payload = {
            'defender_id': user.id,
            'mission_type': 'recon',
            'reconspies': 1
        }

        valid_captcha = self._roc.submit_captcha_url(
            captcha, targeturl, payload, 'roc_spy')

        self._captchamaplock.acquire()
        del self._captchamap[captcha]
        self._usercaptchas[user].remove(captcha)
        self._spystatus[user].active_captchas -= 1
        if valid_captcha:
            self._spystatus[user].solved_captchas += 1
        if self._hit_spy_limit(self._roc.r.text):
            self._handle_maxed_target(user)
        self._captchamaplock.release()

    def start_event(self) -> None:
        if not self._roc.is_logged_in():
            print('Error: Could not start event. ROC is not logged in')
            return

        self._get_all_users()

        if len(self._battlefield) == 0:
            print("Error: could not get battlefield")
            return
        else:
            print(f"Detected {len(self._battlefield)} users.")

        def onsolvecallback(captcha: Captcha) -> Thread:
            t = Thread(target=self._oncaptchasolved, args=[captcha])
            t.start()
            return t

        def getnewcaptchas(desiredcount) -> Thread:
            t = Thread(target=self._getsend_captchas, args=[desiredcount])
            t.start()
            return t

        xcount, ycount = 8, 1
        initcaptchas = self._getnewcaptchas(xcount*ycount*2)

        self._gui = MulticaptchaGUI(
            initcaptchas, onsolvecallback, getnewcaptchas, xcount, ycount)

        self._gui.start_event()


def _bytesimage_to_photoimage_resize(
        image,
        newx: int = 150,
        newy: int = 150
        ) -> PhotoImage:
    nparr = np.frombuffer(image, dtype=np.uint8)
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

        self._update_view_lock = Lock()
        self._modifycaptchas_lock = Lock()

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
        self._update_view_lock.acquire()

        for i in range(min(len(self._captchas), self._captchawindowscount)):
            self._canvases[i].delete('all')
            self._canvases[i].create_image(0, 0,
                                           anchor=NW,
                                           image=self._images[i])

        for i in range(self._captchawindowscount - len(self._captchas)):
            self._canvases[self._captchawindowscount - i-1].delete('all')

        self._update_view_lock.release()

    def _get_new_captchas(self) -> None:
        diff = self._captchawindowscount*2 - len(self._captchas)
        if diff > 0:
            self._getcaptchas(
                self._captchawindowscount*2 - len(self._captchas))

    def __on_keypress(self, event: Event):
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

    def _answer_selected(self, answer: str) -> None:
        if len(self._images) <= 0:
            return

        self._modifycaptchas_lock.acquire()
        self._images.popleft()
        cap = self._captchas.popleft()
        self._modifycaptchas_lock.release()

        cap.ans = answer
        self._onselect(cap)
        self._get_new_captchas()
        self._update_captcha_view()

    def _remove_captcha(self, captcha: Captcha) -> None:
        index = self._captchas.index(captcha)
        del self._captchas[index]
        del self._images[index]

    def add_captchas(self, newcaptchas: List[Captcha]) -> None:
        self._modifycaptchas_lock.acquire()
        print(f'Adding {len(newcaptchas)} captchas')
        no_caps = len(self._images) == 0

        newimgs = self._create_imgs_from_captchas(newcaptchas)
        self._captchas.extend(newcaptchas)
        self._images.extend(newimgs)

        if no_caps:
            self._update_captcha_view()

        self._modifycaptchas_lock.release()

    def remove_captchas(self, captchas: Iterable) -> None:
        self._modifycaptchas_lock.acquire()
        for captcha in captchas:
            self._remove_captcha(captcha)

        self._update_captcha_view()
        self._modifycaptchas_lock.release()

    def start_event(self) -> None:
        self._root.mainloop()

    def end_event(self) -> None:
        self._root.destroy()


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


def runevent_new():
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

    if not login(rochandler, user_settings):
        print('Error logging in.')
        quit()

    skip_idsstr = {str(id) for id in skip_ids}
    onlyspy_idsstr = {str(id) for id in onlyspy_ids}
    event = SpyEvent(rochandler, skip_idsstr, onlyspy_idsstr)
    event.start_event()


# test_multiimage('D:/')
# runevent()
runevent_new()
