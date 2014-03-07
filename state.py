#!/usr/bin/env python
# GpNeWJV9rN


import random
import os


from pygame.sprite           import Sprite
from pygame                  import Surface
from retrogamelib.util       import *
from retrogamelib.camera     import *
from constants                import *


class State(object):

    def __init__(self):
        super(State, self).__init__()

        self.running = True
        self.loaded  = False
        self.change_state = ""
        
        self.surf_main  = Surface(WIN_SIZE)


    def on_load(self, camera=None, font=None, fps=None):
        self.loaded = True
        if camera:
            self.cam = camera
            self.paracam = ParallaxCamera(self.cam, 2, 2)
        if font:
            self.font = font
        if fps:
            self.fps = fps

    def on_resume(self):
        self.running = True
        
    def on_event(self, e):
        pass


    def on_update(self):
        pass


    def on_collision(self):
        pass


    def on_animate(self):
        pass


    def on_render(self):
        pass
