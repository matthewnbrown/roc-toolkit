from numpy import random

# onmousemove = function(e)
# {console.log("mouse location:", e.clientX, e.clientY)}


class ROCCaptchaSelector():
    __btn_dimensions = (40, 30)
    __keypadTopLeft = {'roc_recruit': [890, 705],
                       'roc_armory': [973, 1011],
                       'roc_attack': [585, 680],
                       'roc_spy': [585, 695]}
    __keypadGap = [52, 42]

    def __init__(self, resolution=None) -> None:
        self.resolution = resolution

    def get_xy(self, number):
        pass

    def get_xy_static(self, number, page):
        if page not in self.__keypadTopLeft:
            raise Exception(
                f'Page {page} does not have coordinates for captchas!'
                )
        number = int(number) - 1
        x_btn = self.__keypadTopLeft[page][0] \
            + (number % 3) * self.__keypadGap[0]
        y_btn = self.__keypadTopLeft[page][1] \
            + (number // 3) * self.__keypadGap[1]

        x_click = -x_btn
        while x_click < x_btn or x_click > x_btn + self.__btn_dimensions[0]:
            x_click = x_btn + random.normal(0, self.__btn_dimensions[0]/3)
        y_click = -y_btn
        while y_click < y_btn or y_click > y_btn + self.__btn_dimensions[1]:
            y_click = y_btn + random.normal(0, self.__btn_dimensions[1]/3)

        return (int(x_click), int(y_click))


class ROCCaptchaSelector_deprecated():
    __btn_dimensions = (45, 35)

    __btn_locations = {
        '1': (898, 732), '2': (950, 732), '3': (1003, 732),
        '4': (898, 772), '5': (950, 772), '6': (1003, 772),
        '7': (898, 797), '8': (950, 797), '9': (1003, 797)}

    def __init__(self, resolution=None) -> None:
        self.resolution = resolution

    def get_xy(self, number):
        pass

    def get_xy_static(self, number):
        x_btn = self.__btn_dimensions[0]
        y_btn = self.__btn_dimensions[1]

        x_click = -x_btn
        while x_click < -x_btn//2 or x_click > x_btn//2:
            x_click = random.normal(0, x_btn/4)
        y_click = -y_btn
        while y_click < -y_btn//2 or y_click > y_btn//2:
            y_click = random.normal(0, y_btn/4)

        btn_loc = self.__btn_locations[number]
        x = btn_loc[0]
        y = btn_loc[1]
        return (int(x + x_click), int(y+y_click))
