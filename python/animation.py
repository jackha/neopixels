import datetime

class Animation(object):
    def __init__(self, smiley):
        """ Smiley is an array of frames, see smiley_happy"""
        self.smiley = smiley
        self.nof_frames = len(self.smiley)
        self.index = 0
        self.timeout = datetime.datetime.now()

    def grid_if_update_needed(self):
        now = datetime.datetime.now()
        if now > self.timeout:
            self.index = (self.index + 1) % self.nof_frames
            self.timeout = now + datetime.timedelta(seconds=self.smiley[self.index]['time'])
            return self.smiley[self.index]['smiley']
        return None