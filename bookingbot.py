import argparse
import time
import itchat

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

    def start_wechat(self):
        # itchat.send('start booking bot, input:help, get info', 'filehelper')
        self._book_day = time.localtime(time.time()).tm_mday
        self._book_hour = time.localtime(time.time()).tm_hour
        self._sport_name = 'basketball'
        self._sport_day = 7
        self._sport_hour = [21]
        @itchat.msg_register([itchat.content.TEXT])
        def chat_trigger(msg):
            if msg['Text'] == 'help':
                itchat.send(u'input your user_name', 'filehelper')
                itchat.send(u'example:u=txf', 'filehelper')
                itchat.send(u'input your user_pwd', 'filehelper')
                itchat.send(u'example:p=123', 'filehelper')
                itchat.send(u'input booking day', 'filehelper')
                itchat.send(u'example:bd=15', 'filehelper')
                itchat.send(u'input booking hour', 'filehelper')
                itchat.send(u'example:bh=8', 'filehelper')
                itchat.send(u'input sport name', 'filehelper')
                itchat.send(u'example:sn=basketball', 'filehelper')
                itchat.send(u'input sport day', 'filehelper')
                itchat.send(u'example:sd=7', 'filehelper')
                itchat.send(u'input sport hour', 'filehelper')
                itchat.send(u'example:sh=21 19 15', 'filehelper')
                itchat.send(u'start booking, input:start', 'filehelper')
            elif 'u=' in msg['Text']:
                self._user_name = msg['Text'][2:]
                itchat.send(u'record your name', 'filehelper')
            elif 'p=' in msg['Text']:
                self._user_pwd = msg['Text'][2:]
                itchat.send(u'record your password', 'filehelper')
            elif 'bd=' in msg['Text']:
                self._booking_day = msg['Text'][3:]
            elif 'bh=' in msg['Text']:
                self._booking_hour = msg['Text'][3:]
            elif 'sn=' in msg['Text']:
                self._sport_name = msg['Text'][3:]
            elif 'sd=' in msg['Text']:
                self._sport_day = msg['Text'][3:]
            elif 'sh=' in msg['Text']:
                self._sport_hour = msg['Text'][3:]
            elif msg['Text'] == u'start':
                assert self._user_name is not None
                assert self._user_pwd is not None
                assert self._book_day is not None
                assert self._book_hour is not None
                assert self._sport_name is not None
                assert self._sport_day is not None
                assert self._sport_hour is not None

                while True:
                    daytime = time.localtime(time.time()).tm_mday
                    hourtime = time.localtime(time.time()).tm_hour
                    mintime = time.localtime(time.time()).tm_min
                    print('Now time: {} day {} hour {} min'.format(daytime, hourtime, mintime))
                    if daytime == self._book_day and hourtime == self._book_hour:
                        if self.book(self._sport_hour, self._sport_name, self._sport_day) == 1:
                            itchat.send(u'booking successful', 'filehelper')
                            break
                        else:
                            itchat.send(u'no available time', 'filehelper')
                            self._log_failed()
                            itchat.send_image('failed.jpg', 'filehelper')
                            break
                    else:
                        time.sleep(60)
            else:
                itchat.send(u'input error', 'filehelper')

        itchat.auto_login(hotReload=True)
        # itchat.auto_login()
        itchat.run()

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
            time.sleep(30)
            return 0

        self._confirm_booking()
        self.browser.close()
        return 1

    def _choose_day(self, day):
        assert day < 8
        assert day >= 0
        curr_wday = time.localtime(time.time()).tm_wday
        booking_day = curr_wday + day + 1
        if booking_day > 13:
            booking_day -= 13
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
        self._click(377, 600)
        self.keyboard.type_string(self._user_pwd)
        self.keyboard.tap_key(self.keyboard.enter_key)

    def _click(self, x, y):
        self.mouse.move(x, y)
        time.sleep(1)
        self.mouse.click(x, y, 1, 3)

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

    def _log_failed(self):
        img = ImageGrab.grab()
        img = np.array(img, dtype=np.uint8)
        screen_roi = img[:1080, :1920]
        img = Image.fromarray(screen_roi)
        img.save('failed.jpg')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='sports booking bot')
    parser.add_argument('--user_name', type=str, default=None)
    parser.add_argument('--user_pwd', type=str, default=None)
    parser.add_argument('--book_day', type=int, default=15)
    parser.add_argument('--book_hour', type=int, default=14)
    parser.add_argument('--sport_name', type=str, default='basketball')
    parser.add_argument('--sport_day', type=int, default=7)
    args = parser.parse_args()

    bot = BookingBot(args.user_name, args.user_pwd)
    bot.start_wechat()
    
    # while True:
    #     daytime = time.localtime(time.time()).tm_mday
    #     hourtime = time.localtime(time.time()).tm_hour
    #     mintime = time.localtime(time.time()).tm_min
    #     print('Now time: {} day {} hour {} min'.format(daytime, hourtime, mintime))
    #     if daytime == args.book_day and hourtime == args.book_hour:
    #         if bot.book(range(21, 7, -1), args.sport_name, args.sport_day) == 1:
    #             break
    #     else:
    #         time.sleep(60)
