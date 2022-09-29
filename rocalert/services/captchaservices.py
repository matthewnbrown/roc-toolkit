from collections import deque
from functools import partial
from threading import Lock, Condition, Thread
from tkinter import Entry, Canvas, Button, Frame, PhotoImage, Tk, NW, Event
from PIL import Image, ImageTk
import cv2
import numpy as np
from typing import Callable, Iterable, List
from requests import Response
from rocalert.roc_web_handler import RocWebHandler
from rocalert.roc_web_handler import Captcha


class GetCaptchaService:
    @classmethod
    def run_service(cls, response: Response, roc: RocWebHandler) -> Captcha:
        """_summary_
            Retrieves a captcha from a page
        Args:
            page_text (str): _description_
                Response text from the page where the captcha is located
        Raises:
            Exception: _description_
                ROC is None
            Exception: _description_
                response is None
        Returns:
            Captcha: _description_
                Captcha pulled from page.
                Will be None if no captcha is detected
        """

        if roc is None:
            raise Exception('ROC parameter must exist')
        elif response is None:
            raise Exception('Response parameter must exist')

        captcha_type = cls._detectcaptchatype(response)

        if captcha_type == Captcha.CaptchaType.IMAGE:
            return cls._get_img_captcha(response)
        if captcha_type == Captcha.CaptchaType.EQUATION:
            return cls._get_equation_captcha(response)
        if captcha_type == Captcha.CaptchaType.TEXT:
            return cls._get_text_captcha(response)

        return None

    @classmethod
    def _get_img_hash(cls, pagetext: str) -> str:
        index = pagetext.find('img.php?hash=')
        if index == -1:
            return None
        endIndex = pagetext.find('"', index, index+100)
        imghash = pagetext.text[index + len('img.php?hash='): endIndex]
        return imghash

    @classmethod
    def _get_img_captcha(cls, resp: Response, roc: RocWebHandler) -> Captcha:
        imghash = cls._get_img_hash(resp.text)
        imgbytes = roc.get_imgcap_from_hash(imghash)
        return Captcha(imghash, imgbytes, captype=Captcha.CaptchaType.IMAGE)

    @classmethod
    def _get_equation_captcha(cls, resp: Response) -> Captcha:
        index = resp.text.find('<h1>What is')
        if index == -1:
            return None
        endIndex = resp.text.find('</h1>', index, index+100)
        equation = resp.text[index + len('<h1>What is'):  endIndex]
        equation = equation.strip()[:-1]
        return Captcha(equation, captype=Captcha.CaptchaType.EQUATION)

    @classmethod
    def _get_text_captcha(cls, resp: Response, roc: RocWebHandler) -> Captcha:
        return Captcha('TEXT', captype=Captcha.CaptchaType.TEXT)

    @classmethod
    def _has_text_cap(cls, response: Response) -> bool:
        return 'cooldown' in response.url

    @classmethod
    def _has_img_cap(cls, response: Response) -> bool:
        return '[click the correct number to proceed]' in response.text

    @classmethod
    def _has_equation_cap(cls, response: Response) -> bool:
        return '<h1>What is' in response.text

    @classmethod
    def _detectcaptchatype(cls, response: Response) -> Captcha.CaptchaType:
        if cls._has_text_cap(response):
            return Captcha.CaptchaType.TEXT
        if cls._has_img_cap(response):
            return Captcha.CaptchaType.IMAGE
        if cls._has_equation_cap(response):
            return Captcha.CaptchaType.EQUATION
        return None


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
        self._newcaptchas = Condition()

        self._end_event = False
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
        if self._end_event:
            self._end()
            return

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

    def _waitforcaps(self) -> None:
        self._newcaptchas.acquire()
        def cond(): return self._available_image()
        print("No captchas to show, waiting for delivery")
        self._newcaptchas.wait_for(cond)
        print('Received captcha delivery, updating')
        self._update_captcha_view()
        self._newcaptchas.release()

    def _answer_selected(self, answer: str) -> None:
        self._newcaptchas.acquire()
        if len(self._images) == 0:
            self._newcaptchas.release()
            return

        self._images.popleft()
        cap = self._captchas.popleft()

        if not self._available_image():
            t = Thread(target=self._waitforcaps)
            t.start()

        self._newcaptchas.release()

        cap.ans = answer
        self._onselect(cap)
        self._get_new_captchas()
        self._update_captcha_view()

    def add_captchas(self, newcaptchas: List[Captcha]) -> None:
        newimgs = self._create_imgs_from_captchas(newcaptchas)
        self._newcaptchas.acquire()
        self._captchas.extend(newcaptchas)
        self._images.extend(newimgs)

        self._newcaptchas.notify_all()
        self._newcaptchas.release()

    def start(self) -> None:
        self._root.mainloop()

    def signal_end(self) -> None:
        self._end_event = True

    def _end(self) -> None:
        self._root.destroy()
