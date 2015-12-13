# a test host program for my 16x8 neopixel display!
# "comport": "/dev/tty.usbmodemfd12111",
# "baudrate": "115200"
# python 3

from serial import Serial
import time
import smiley
from animation import Animation
from font import tiny_font
from image import LoFiImage
import datetime
import os
import json

COM_PORT = "/dev/tty.usbmodemfd12111"
BAUD_RATE = 115200
COM_TIMEOUT = 1000

Y = 8
X = 16

NUM_PIX = X * Y

MULTIPLIERS_BY_HOUR = [
    0.4, 0.4, 0.4, 0.4, 0.4, 0.4, 
    0.4, 0.4, 0.7, 1, 1.5, 1.5,
    1.5, 1.5, 1.5, 1.5, 1.5, 1.0,
    1, 1, 1, 1, 0.7, 0.7]


class NeopixelSerial(Serial):

    def __init__(self, *args, **kwargs):
        result = super(NeopixelSerial, self).__init__(*args, **kwargs)
        self.buffer = [0] * NUM_PIX * 3
        self.last_update = time.time()
        self.last_buffer = None  # used to check if something has changed
        return result

    def wipe_buffer(self):
        self.buffer = [0] * NUM_PIX * 3

    def wipe(self, r=0, g=0, b=0):
        msg_lst = []
        for i in range(NUM_PIX):
            msg_lst.extend([b, g, r])
        msg = bytes(msg_lst) 
        self.write(msg)

    def update(self):
        """Flush my buffer to neopixels."""
        if self.last_buffer == self.buffer:
            # nothing has changed
            return
        while time.time() < self.last_update + 0.04:
            time.sleep(0.001)
        msg = bytes(self.buffer)
        self.write(msg)
        self.last_update = time.time()
        self.last_buffer = self.buffer.copy()

    def bitmap(self, x, y, arr, r=10, g=0, b=0):
        """'plot' array to x, y"""
        for yi, yv in enumerate(arr):
            for xi, xv in enumerate(yv):
                self.pix(x + xi, y + yi, xv*r, xv*g, xv*b)

    def bitmap2(self, x, y, arr, r=10, g=0, b=0, size_x=3):
        """'plot' array with bits to x, y. see font.py"""
        for yi, yv in enumerate(arr):
            yv <<= 1  # place a 0 behind
            x_pos = size_x - 1
            while yv > 0:
                v = yv % 2  # 0 or 1
                yv >>= 1
                self.pix(x + x_pos, y + yi, v*r, v*g, v*b)
                x_pos -= 1

    def color_bitmap(self, x, y, arr):
        """plot color bitmap arr: x, y, (r, g, b)"""
        for yi, yv in enumerate(arr):
            for xi, xv in enumerate(yv):
                self.pix(x + xi, y + yi, xv[0], xv[1], xv[2])

    def text(self, x, y, text, font, r=5, g=0, b=0):
        x_pos = 0
        size_x = font['size_x']
        for c in text:
            ch = c.lower()
            bitmap = font.get(ch, font['default'])
            if ch in {'.', ' '}:
                size_x_ = 1
            elif ch in {'(', ')', ':', '!'}:
                size_x_ = 2
            else:
                size_x_ = size_x + 1
            self.bitmap2(x + x_pos, y, bitmap, r=r, g=g, b=b, size_x=size_x_)
            x_pos += size_x_

    def colorful_text(self, x, y, text, font, colors):
        """Colors is a list of 3-tuples for all the colors.
        i.e. [(3, 0, 0), (10,10,10), (0,10,13)]
        """
        x_pos = 0
        color_idx = 0
        size_x = font['size_x']
        for c in text:
            ch = c.lower()
            bitmap = font.get(ch, font['default'])
            if ch in {'.', ' '}:
                size_x_ = 1
            elif ch in {'(', ')', ':', '!'}:
                size_x_ = 2
            else:
                size_x_ = size_x + 1
            r, g, b = colors[color_idx]
            self.bitmap2(x + x_pos, y, bitmap, r=r, g=g, b=b, size_x=size_x_)
            x_pos += size_x_
            color_idx += 1
            if color_idx >= len(colors):
                color_idx = 0

    def pix(self, x, y, r, g, b):
        """plot a single pixel to the buffer"""
        if x < 0 or x > 15 or y < 0 or y > 7:
            return
        if x < 8:
            i = 3 * (y * 8 + x)
        elif x >= 8:
            i = 3 * (64 + (x - 8) + y * 8)
        self.buffer[i] = b
        self.buffer[i + 1] = g
        self.buffer[i + 2] = r

    def neo_text(self, nt, multiplier=1.0):
        """Draw NeoText object"""
        self.text(
            nt.x, nt.y, nt.text, nt.font, 
            r=int(nt.color[0] * multiplier), 
            g=int(nt.color[1] * multiplier), 
            b=int(nt.color[2] * multiplier))


class NeoText(object):
    """Colorful text that lives on the screen"""
    def __init__(self, text='', color=(5,0,0), x=0, y=1, font=None):
        self.text = text
        self.color = color
        self.x = x
        self.y = y
        self.font = font


if __name__ == '__main__':
    if os.path.exists('settings.json'):
        with open('settings.json', 'r') as f:
            settings = json.load(f)
            com_port = settings['com_port']
    else:
        com_port = COM_PORT
    baud_rate = BAUD_RATE
    com_timeout = COM_TIMEOUT
    neo = NeopixelSerial(
        port=com_port, baudrate=baud_rate, 
        timeout=com_timeout)

    time.sleep(2)  # allow arduino to restart and initialize

    ani1 = Animation(smiley.pacman_anim)
    ani2 = Animation(smiley.ghost_anim)
    ani_beer1 = Animation(smiley.beer1_anim)
    ani_beer2 = Animation(smiley.beer2_anim)
    # For pac-man animation
    r1, g1, b1 = 3, 3, 0
    r2, g2, b2 = 3, 0, 3
    x = 0
    txt_coffee = 'coffee time!!! '

    im_mario = LoFiImage(size_x=X, size_y=Y, multiplier=0.10, gamma_adjust=-30)
    im_mario.load("mario.png")

    neo_text = []
    x_pos = [0, 4, 8, 9, 13, 0, 4, 8, 9, 13]
    y_pos = [1, 1, 1, 1, 1, 9, 9, 9, 9, 9]
    for i in range(10):
        neo_text.append(NeoText(color=(3,0,0), x=x_pos[i], y=y_pos[i], font=tiny_font))

    txt = 'aaaaa'
    old_txt = 'bbbbb'

    t = datetime.datetime.now()
    t_old_temp = t
    old_t = t

    while 1:
        t_old_temp = t
        t = datetime.datetime.now()
        if t.second != t_old_temp.second:
            old_t = t_old_temp

        if t.second % 2 == 0:
            txt = t.strftime('%H.%M')
        else:
            txt = t.strftime('%H %M')
        if old_t.second % 2 == 0:
            old_txt = old_t.strftime('%H.%M')
        else:
            old_txt = old_t.strftime('%H %M')

        for i, c in enumerate(old_txt):  # prepare for transitions
            neo_text[i].text = c
            neo_text[i].y = 9
        for i, c in enumerate(txt):
            neo_text[i + 5].text = c
            neo_text[i + 5].y = 1

        if t.second == 0:
            #neo_text[5+4].color = (3+(t.microsecond) // 50000, 0, 0)
            #neo_text[4].color = (3, 0, 0)
            new_y = 1 + (1000000 - t.microsecond) // 100000
            old_y = 1 - t.microsecond // 100000
            neo_text[5+4].y = new_y
            neo_text[4].y = old_y
            
            if t.minute % 10 == 0:
                #neo_text[5+3].color = (3+(t.microsecond) // 50000, 0, 0)
                #neo_text[3].color = (3, 0, 0)
                neo_text[5+3].y = new_y
                neo_text[3].y = old_y
            if t.minute == 0:
                # neo_text[5+1].color = (3+(t.microsecond) // 50000, 0, 0)
                # neo_text[1].color = (3, 0, 0)
                neo_text[5+1].y = new_y
                neo_text[1].y = old_y
            if t.hour % 10 == 0:
                # neo_text[5+0].color = (3+(t.microsecond) // 50000, 0, 0)
                # neo_text[0].color = (3, 0, 0)
                neo_text[5+0].y = new_y
                neo_text[0].y = old_y

        if t.hour == 23 and t.minute == 59:
            new_grid1 = ani1.grid_if_update_needed()
            if new_grid1 is not None:
                neo.bitmap(0, 0, new_grid1, r1, g1, b1)
            new_grid2 = ani2.grid_if_update_needed()
            if new_grid2 is not None:
                neo.bitmap(8, 0, new_grid2, r2, g2, b2)
        elif t.minute == 59 and t.second == 59:
            # mario animation every hour
            for ii in range(32):
                bitmap = im_mario.crop_bitmap(
                    0, -8+ii)
                neo.color_bitmap(0, 0, bitmap)
                neo.update()
        elif t.hour == 1 and t.minute == 30:
            # the infamous coffeetime
            neo.text(x, 1, txt_coffee, tiny_font, g=10)
            x -= 1
            if x < -len(txt_coffee) * 4:
                x = 17
        elif t.hour == 4 and t.minute == 0:
            # vier uur = bier uur
            new_grid1 = ani_beer1.grid_if_update_needed()
            if new_grid1 is not None:
                neo.bitmap(0, 0, new_grid1, r=50, g=50, b=0)
            new_grid2 = ani_beer2.grid_if_update_needed()
            if new_grid2 is not None:
                neo.bitmap(8, 0, new_grid2, r=50, g=50, b=0)
        else:
            neo.wipe_buffer()
            for nt in neo_text:
                neo.neo_text(nt, multiplier=MULTIPLIERS_BY_HOUR[t.hour])

        neo.update()
        time.sleep(0.1)