#!/usr/bin/env python
"""
Things todo:
    Add functionality to menu buttons

    clean up the map's XML
    
    More Documentation
"""

import pygame
import random
import os

from constants               import WIN_SIZE, CAPTION, FONT_DIR
from utils                   import Timer
from scene                   import Scene

class Game(object):

    def __init__(self):
        super(Game, self).__init__()
        
        pygame.init()
        self.surf_main = pygame.display.set_mode(WIN_SIZE)
        pygame.display.set_caption(CAPTION)
        self.debug = False
        self.running = True
        
        self.scenes = {"scene1": Scene()}
        self.curr_scene = self.scenes["scene1"]


    def on_load(self):
        self.curr_scene.on_load()


    def on_reset(self):
        self.curr_scene.on_reset()


    def on_event(self):
        self.events = pygame.event.get()
        
        for e in self.events:
            if e.type == pygame.QUIT:
                self.running = False
            elif e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE:
                    self.running = False
        
        self.curr_scene.on_event(self.events)
    
    def on_update(self):
        self.curr_scene.on_update()
    
    def on_render(self):
        self.curr_scene.on_render()

    def on_execute(self):
        self.on_load()
        while self.running == True:
            self.on_event()
            self.on_update()
            self.on_render()
            
            pygame.display.update()
            self.surf_main.fill((80,80,100, 255))
            



if __name__ == '__main__':
    random.seed()
    Game().on_execute();
