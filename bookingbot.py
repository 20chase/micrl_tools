import argparse
import time

import numpy as np
import pyscreenshot as ImageGrab

from selenium import webdriver
from pykeyboard import PyKeyboard
from pymouse import PyMouse
from PIL import Image


class BookingBot(object):
    def __init__(self, user_name, user_pwd):
        self._user_name = user_name
        self._user_pwd = user_pwd
        self.keyboard = PyKeyboard()
        self.mouse = PyMouse()
        
    def _login(self):
        self.browser = webdriver.Firefox()
        self.browser.set_window_size(1920, 1080)
        self.browser.set_window_position(0, 0)
        self.browser.get('http://www.cityu.edu.hk/sfbi-std/fbi_fp.htm')
        time.sleep(2)
        self.keyboard.type_string(self._user_name)
        self.keyboard.tap_key(self.keyboard.tab_key)
        self.keyboard.type_string(self._user_pwd)
        self.keyboard.tap_key(self.keyboard.enter_key)
        time.sleep(2)
        self._click(350, 40, 2)
        time.sleep(2)

    def book(self, sport_hours, sport_name='basketball', sport_day=7):
        self._login()
        self._choose_day(sport_day)
        self._choose_sport(sport_name)
        time.sleep(3)
        labels = self._get_access_lable()

        for hour in sport_hours:
            if labels[hour-8]:
                self._choose_hour(hour)
                break
        else:
            print('Sorry, no available time')
            self.browser.close()
            time.sleep(5)
            return 0

        self._confirm_booking()
        self.browser.close()
        return 1

    def _choose_day(self, day):
        assert day < 8
        assert day >= 0
        curr_wday = time.localtime(time.time()).tm_wday
        booking_day = curr_wday + day + 1
        if booking_day > 6:
            pos = self._get_day_pos(1, (booking_day - 7))
        else:
            pos = self._get_day_pos(0, booking_day)

        self._click(pos[0], pos[1]) 
        time.sleep(1)

    def _choose_sport(self, sport):
        # you need to add the sport you want
        if sport == 'basketball':
            self._click(1075, 460)

        time.sleep(1)

    def _choose_hour(self, hour):
        hour = hour - 8
        pos = self._get_hour_pos(hour)
        self._click(pos[0], pos[1])
        time.sleep(1)

    def _confirm_booking(self):
        self._click(377, 610)
        self.keyboard.type_string(self._user_pwd)
        self.keyboard.tap_key(self.keyboard.enter_key)

    def _click(self, x, y, times=3):
        self.mouse.move(x, y)
        time.sleep(1)
        self.mouse.click(x, y, 1, times)

    def _get_day_pos(self, row ,column):
        return [300 + column * 27, 470 + row * 30]

    def _get_hour_pos(self, row):
        return [368, 316 + row * 23]

    def _get_access_lable(self):
        img = ImageGrab.grab()
        b, g, r = img.split()
        img = Image.merge("RGB", (r, g, b))
        img = np.array(img, dtype=np.uint8)
        roi = img[315:624, 350:379]
        flags = []
        for i in range(14):
            sub_roi = roi[i*22:(i+1)*22, :]
            blue = sub_roi[sub_roi.shape[0] // 2, sub_roi.shape[1] // 2, 0]
            if blue > 120:
                flag = True
            else:
                flag = False 

            flags.append(flag)

        return flags

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='sports booking bot')
    parser.add_argument('--user_name', type=str, default=None)
    parser.add_argument('--user_pwd', type=str, default=None)
    parser.add_argument('--book_day', type=int, default=13)
    parser.add_argument('--book_hour', type=int, default=21)
    parser.add_argument('--sport_name', type=str, default='basketball')
    parser.add_argument('--sport_day', type=int, default=7)
    args = parser.parse_args()

    bot = BookingBot(args.user_name, args.user_pwd)
    while True:
        daytime = time.localtime(time.time()).tm_mday
        hourtime = time.localtime(time.time()).tm_hour
        mintime = time.localtime(time.time()).tm_min
        print('Now time: {} day {} hour {} min'.format(daytime, hourtime, mintime))
        if daytime == args.book_day and hourtime == args.book_hour:
            if bot.book([15], args.sport_name, args.sport_day) == 1:
                break
        else:
            time.sleep(60)
