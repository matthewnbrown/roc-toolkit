from typing import Callable, Iterable
from collections import deque
from functools import partial
from threading import Lock, Condition
from tkinter import Entry, Canvas, Button, Frame, PhotoImage, Tk, NW, Event
from PIL import Image, ImageTk
import cv2
import numpy as np

from rocalert.roc_web_handler import Captcha


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
            captchas: list[Captcha],
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
        self._newcaptchas = Condition()

        self._event_over = False
        self._root.bind('<<end_event>>', self._end)
        self._root.bind('<<newcaptchas>>', self._newcaptcha_event)
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
                                   ) -> list[Captcha]:
        res = []
        for captcha in captchas:
            res.append(_bytesimage_to_photoimage_resize(captcha.img))
        return res

    @property
    def _captchawindowscount(self) -> int:
        return self._xcaptchacount * self._ycaptchacount

    def _update_captcha_view(self) -> None:
        self._newcaptchas.acquire()
        for i in range(min(len(self._captchas), self._captchawindowscount)):
            self._canvases[i].delete('all')
            self._canvases[i].create_image(0, 0,
                                           anchor=NW,
                                           image=self._images[i])

        for i in range(self._captchawindowscount - len(self._captchas)):
            self._canvases[self._captchawindowscount - i-1].delete('all')
        self._newcaptchas.release()

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

    def _available_image(self) -> bool:
        return len(self._images) > 0

    def _answer_selected(self, answer: str) -> None:
        self._newcaptchas.acquire()
        if len(self._images) == 0:
            self._newcaptchas.release()
            return

        self._images.popleft()
        cap = self._captchas.popleft()

        self._newcaptchas.release()

        cap.ans = answer
        self._onselect(cap)
        self._get_new_captchas()
        self._update_captcha_view()

    def _newcaptcha_event(self, event: Event) -> None:
        self._update_captcha_view()

    def add_captchas(self, newcaptchas: list[Captcha]) -> None:
        if not self._event_over:
            newimgs = self._create_imgs_from_captchas(newcaptchas)
            self._newcaptchas.acquire()
            self._captchas.extend(newcaptchas)
            self._images.extend(newimgs)

            self._newcaptchas.notify_all()
            self._newcaptchas.release()
            self._root.event_generate('<<newcaptchas>>')

    def start(self) -> None:
        self._root.mainloop()

    def signal_end(self) -> None:
        self._event_over = True
        self._root.event_generate('<<end_event>>')

    def _end(self, event: Event) -> None:
        self._root.destroy()
