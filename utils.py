import pygame
import os

from constants import SCALE


def file_path(path):
    if "/" in path:
        path = path.split("/")
    elif "\\" in path:
        path = path.split("\\")
    if type(path) is type([]):
        return os.path.join(*path)
    else:
        return os.path.join(path)


IMAGES = {}


def load_image(filename):
    if filename not in IMAGES:
        new_image = pygame.image.load(file_path(filename))
        new_image = pygame.transform.scale(
            new_image, (new_image.get_width() * SCALE,
                        new_image.get_height() * SCALE
                        )
        )
        new_image.convert_alpha()
        IMAGES[filename] = new_image

    return IMAGES[filename]


def play_music(filename, loop=0, volume=1.0):
    pygame.mixer.music.load(file_path(filename))
    pygame.mixer.music.set_volume(volume)
    pygame.mixer.music.play(loop)


SOUNDS = {}
SND_VOLUME = 1.0


def play_sound(filename, volume=1.0):
    if filename not in SOUNDS:
        SOUNDS[filename] = pygame.mixer.Sound(file_path(filename))
        SOUNDS[filename].set_volume(SND_VOLUME * volume)
    SOUNDS[filename].play()


def set_global_sound_volume(volume):
    global SND_VOLUME
    SND_VOLUME = volume


def check_collision(obj1, obj2):
    """checks if two objects have collided, using hitmasks"""
    try:
        rect1, rect2, hm1, hm2 = obj1.rect, obj2.rect, obj1.hitmask, obj2.hitmask
    except AttributeError:
        return False
    rect = rect1.clip(rect2)
    if rect.width == 0 or rect.height == 0:
        return False
    x1, y1, x2, y2 = rect.x - rect1.x, rect.y - rect1.y, rect.x - rect2.x, rect.y - rect2.y
    for x in xrange(rect.width):
        for y in xrange(rect.height):
            if hm1[x1 + x][y1 + y] and hm2[x2 + x][y2 + y]:
                return True
            else:
                continue
    return False


def get_colorkey_hitmask(image, rect, key=None):
    """returns a hitmask using an image's colorkey.
       image->pygame Surface,
       rect->pygame Rect that fits image,
       key->an over-ride color, if not None will be used instead of the image's colorkey"""
    if key == None:
        colorkey = image.get_colorkey()
    else:
        colorkey = key
    mask = []
    for x in range(rect.width):
        mask.append([])
        for y in range(rect.height):
            mask[x].append(not image.get_at((x, y)) == colorkey)
    return mask


def get_alpha_hitmask(image, rect, alpha=0):
    """returns a hitmask using an image's alpha.
       image->pygame Surface,
       rect->pygame Rect that fits image,
       alpha->the alpha amount that is invisible in collisions"""
    mask = []
    for x in range(rect.width):
        mask.append([])
        for y in range(rect.height):
            mask[x].append(not image.get_at((x, y))[3] == alpha)
    return mask


def get_colorkey_and_alpha_hitmask(image, rect, key=None, alpha=0):
    """returns a hitmask using an image's colorkey and alpha."""
    mask = []
    for x in range(rect.width):
        mask.append([])
        for y in range(rect.height):
            mask[x].append(not (image.get_at((x, y))[3] == alpha or \
                                image.get_at((x, y)) == colorkey))
    return mask


def get_full_hitmask(image, rect):
    """returns a completely full hitmask that fits the image,
       without referencing the images colorkey or alpha."""
    mask = []
    for x in range(rect.width):
        mask.append([])
        for y in range(rect.height):
            mask[x].append(True)
    return mask


class Timer(object):
    """ A class that updates fps and delta time between frames """

    def __init__(self):
        super(Timer, self).__init__()

        self.old_time = 0
        self.curr_time = 0
        self.last_time = 0
        self.diff_time = 0
        self.speed_factor = 0
        self.num_frames = 0
        self.frames = 0

    def on_update(self):
        self.curr_time = pygame.time.get_ticks()
        self.diff_time = self.curr_time - self.last_time

        if self.curr_time > self.old_time + 1000.:
            self.old_time = self.curr_time
            self.frames = self.num_frames
            self.num_frames = 0

        self.speed_factor = self.diff_time / 100.
        if self.speed_factor > 1:
            self.speed_factor = 1
        self.last_time = self.curr_time
        self.num_frames += 1

    def get_current_time(self):
        return self.curr_time


FPS = Timer()
