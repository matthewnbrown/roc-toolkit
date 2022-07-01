from functools import partial
from tkinter import Entry, Canvas, Button, Frame, PhotoImage, Tk, NW
from PIL import Image, ImageTk  # py -m pip install pillow
import io


class GUI():
    def __init__(self, root, img) -> None:
        self.root = root
        self.entry = Entry(self.root)
        self.user_num_selection = '0'

        self.root.bind("<Key>", self.__on_keypress)
        self.canvas = Canvas(self.root, height=300, width=300)
        self.canvas.grid(row=0, column=0)

        frame = Frame(self.root)
        frame.grid(row=1, column=0)

        self.__add_buttons(frame)
        self.canvas.create_image(0, 0, anchor=NW, image=img)

    def __on_button_click(self, num_str):
        self.__set_selection_close(num_str)

    def __on_keypress(self, event):
        key = event.keysym
        if key.isnumeric and int(key) > 0:
            self.__set_selection_close(key)

    def __set_selection_close(self, num_str):
        self.user_num_selection = num_str
        self.root.destroy()

    def __add_buttons(self, root):
        rows = 3
        cols = 3
        for i in range(rows):
            for j in range(cols):
                num = str(i*(rows) + j+1)
                action_with_arg = partial(self.__on_button_click, num)
                but = Button(root, text=num, command=action_with_arg)
                but.grid(row=i, column=j)

    def get_user_selection(self) -> str:
        return self.user_num_selection


def bytesimage_to_photoimage(image) -> PhotoImage:
    img = Image.open(io.BytesIO(image))
    photoimage = ImageTk.PhotoImage(img)
    return photoimage


def get_user_answer_captcha(image) -> str:
    root = Tk()
    img = bytesimage_to_photoimage(image)
    gui = GUI(root, img)
    root.mainloop()
    return gui.get_user_selection()
