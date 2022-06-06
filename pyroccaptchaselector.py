from numpy import random # py -m pip install numpy

class ROCCaptchaSelector():
    __btn_dimensions = (45, 35)
    __btn_locations = { 
        '1': (898, 732), '2': (950, 732), '3': (1003, 732), 
        '4': (898, 772), '5': (950, 772), '6': (1003, 772), 
        '7': (898, 797), '8': (950, 797), '9': (1003, 797) }

    def __init__ (self, resolution = None) -> None:
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
