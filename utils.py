import pygame
import os

from constants import SCALE


def filepath(path):
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
        new_image = pygame.image.load(filepath(filename))
        new_image = pygame.transform.scale(
            new_image, (new_image.get_width() * SCALE,
                        new_image.get_height() * SCALE
                        )
        )
        new_image.convert_alpha()
        IMAGES[filename] = new_image

    return IMAGES[filename]


def play_music(filename, loop=0, volume=1.0):
    pygame.mixer.music.load(filepath(filename))
    pygame.mixer.music.set_volume(volume)
    pygame.mixer.music.play(loop)

SOUNDS = {}
SND_VOLUME = 1.0


def play_sound(filename, volume=1.0):
    if filename not in SOUNDS:
        SOUNDS[filename] = pygame.mixer.Sound(filepath(filename))
        SOUNDS[filename].set_volume(SND_VOLUME * volume)
    SOUNDS[filename].play()


def set_global_sound_volume(volume):
    global SND_VOLUME
    SND_VOLUME = volume


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
