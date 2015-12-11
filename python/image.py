#
from PIL import Image
from PIL import ImageFilter


class LoFiImage(object):
    """
    Convert hi res pictures to a full color lo-fi representation for the 
    neopixel display
    """
    def __init__(self, size_x, size_y, multiplier=1, gamma_adjust=0):
        self.size_x = size_x
        self.size_y = size_y
        self.im = None
        # color translation
        self.mult = dict((i, max(min(int((i+gamma_adjust)*multiplier), 255), 0)) for i in range(256))

    def load(self, filename):
        self.im = Image.open(filename)
        self.im = self.im.convert('RGB')
        # self.im = self.im.filter(ImageFilter.BLUR)
        
    def to_bitmap(self, x0, y0, x1, y1):
        """scale image and return buffer"""
        #im = self.im.copy()
        #im.thumbnail((self.size_x * 2, self.size_y * 2), Image.ANTIALIAS)
        #im_size_x, im_size_y = im.size
        
        
        orig_size_x = x1 - x0
        orig_size_y = y1 - y0
        step_x = orig_size_x // self.size_x
        step_y = orig_size_y // self.size_y
        bitmap = []
        for y in range(self.size_y):
            row = []
            for x in range(self.size_x):
                r, g, b = 0, 0, 0
                src_x = x0 + x * step_x
                src_y = y0 + y * step_y
                if (
                    src_x < self.im.size[0] and src_x >= 0 and 
                    src_y < self.im.size[1] and src_y >= 0):

                    r, g, b = self.im.getpixel((src_x, src_y))
                pix = (self.mult[r], self.mult[g], self.mult[b])
                row.append(pix)
            bitmap.append(row)
        return bitmap

    def crop_bitmap(self, x0, y0, size_x=None, size_y=None):
        """Crop picture from x0, y0 in size_x, size_y"""
        if size_x is None:
            size_x = self.size_x
        if size_y is None:
            size_y = self.size_y
        bitmap = []
        for y in range(size_y):
            row = []
            for x in range(size_x):
                r, g, b = 0, 0, 0
                src_x = x0 + x
                src_y = y0 + y
                if (
                    src_x < self.im.size[0] and src_x >= 0 and 
                    src_y < self.im.size[1] and src_y >= 0):

                    r, g, b = self.im.getpixel((src_x, src_y))
                pix = (self.mult[r], self.mult[g], self.mult[b])
                row.append(pix)
            bitmap.append(row)
        return bitmap
