# a test host program for my 16x8 neopixel display!
# "comport": "/dev/tty.usbmodemfd12111",
# "baudrate": "115200"
# python 3

from serial import Serial
import time
import smiley
from animation import Animation
from font import tiny_font
import datetime
import os
import json

COM_PORT = "/dev/tty.usbmodemfd12111"
BAUD_RATE = 115200
COM_TIMEOUT = 1000

Y = 8
X = 16

NUM_PIX = X * Y

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
    

if __name__ == '__main__':
    if os.path.exists('settings.json'):
        with open('settings.json', 'r') as f:
            settings = json.load(f)
            com_port = settings['com_port']
    else:
        com_port = COM_PORT
    print("com port: %s" % com_port)
    baud_rate = BAUD_RATE
    print("baud rate: %s" % baud_rate)
    com_timeout = COM_TIMEOUT
    print("timeout: %s" % com_timeout)
    neo = NeopixelSerial(
        port=com_port, baudrate=baud_rate, 
        timeout=com_timeout)

    time.sleep(2)  # allow arduino to restart and initialize

    ani1 = Animation(smiley.pacman_anim)
    ani2 = Animation(smiley.ghost_anim)
    ani_beer1 = Animation(smiley.beer1_anim)
    ani_beer2 = Animation(smiley.beer2_anim)
    r1, g1, b1 = 5, 5, 0
    r2, g2, b2 = 5, 0, 5
    x = 0
    txt_coffee = 'coffee time!!! '

    while 1:
        t = datetime.datetime.now()
        if t.second % 2 == 0:
            txt = t.strftime('%H.%M')
        else:
            txt = t.strftime('%H %M')
        colors = [(3, 0, 0), (3, 0, 0), (3, 0, 0), (3, 0, 0), (3, 0, 0)]
        if t.second == 59:
            colors[4] = (3+(t.microsecond) // 50000, 0, 0)
            if t.minute % 10 == 9:
                colors[3] = (3+(t.microsecond) // 50000, 0, 0)
            if t.minute == 59:
                colors[1] = (3+(t.microsecond) // 50000, 0, 0)
            if t.hour % 10 == 9:
                colors[0] = (3+(t.microsecond) // 50000, 0, 0)
                
        if t.hour == 23 and t.minute == 59:
            new_grid1 = ani1.grid_if_update_needed()
            if new_grid1 is not None:
                neo.bitmap(0, 0, new_grid1, r1, g1, b1)
            new_grid2 = ani2.grid_if_update_needed()
            if new_grid2 is not None:
                neo.bitmap(8, 0, new_grid2, r2, g2, b2)
        elif t.hour == 1 and t.minute == 30:
            neo.text(x, 1, txt_coffee, tiny_font, g=10)
            x -= 1
            if x < -len(txt_coffee) * 4:
                x = 17
        elif t.hour == 4 and t.minute == 0:
            new_grid1 = ani_beer1.grid_if_update_needed()
            if new_grid1 is not None:
                neo.bitmap(0, 0, new_grid1, r=50, g=50, b=0)
            new_grid2 = ani_beer2.grid_if_update_needed()
            if new_grid2 is not None:
                neo.bitmap(8, 0, new_grid2, r=50, g=50, b=0)
        else:
            neo.wipe_buffer()
            neo.colorful_text(0, 1, txt, tiny_font, colors)
        # seconds bar, ugly...
        # neo.pix(0, 7, 0, 1, 0)
        # for i in range(t.second // 4):
        #     neo.pix(i + 1, 7, 0, 1, 0)
        neo.update()
        time.sleep(0.1)

    # when the program quits, the arduino is reset again.
    #import pdb; pdb.set_trace()