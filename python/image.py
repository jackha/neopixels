#
from PIL import Image


class LoFiImage(object):
    """
    Convert hi res pictures to a full color lo-fi representation for the 
    neopixel display
    """
    def __init__(self, size_x, size_y):
        self.buffer = 3 * [0] * target_x * target_y
        self.size_x = size_x
        self.size_y = size_y
        self.im = None

    def load_img(self, filename):
        self.im = Image.open(filename)
        
    def to_buffer(self, x0, y0, x1, y1):
        """scale image and return buffer"""
        pass
