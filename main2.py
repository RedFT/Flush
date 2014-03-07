#!/usr/bin/env python
"""
Things todo:
    Add functionality to menu buttons

    clean up the map's XML
    
    Add more comments
"""

import pygame
import random
import os


from pygame.sprite           import Sprite
from pygame                  import font
from data                    import *
from utils                   import *
from constants               import *
from retrogamelib.camera     import *
from playstate               import PlayState
from pausestate              import PauseState


class Game(object):
    """ "The Game Engine" """

    def __init__(self):
        super(Game, self).__init__()
        pygame.init()
        
        self.debug = False
        self.running = True
        
        self.fps = Timer()
        self.font = font.Font(FONT_DIR + "Terminus.ttf", 14)
        
        pygame.display.set_caption(CAPTION);
        self.surf_main = pygame.display.set_mode(WIN_SIZE)

        self.playstate = PlayState()
        self.pausestate = PauseState()
        self.states = {'playstate'  : self.playstate,
                      'pausestate' : self.pausestate}

        self.state_curr = self.states['playstate']

        self.cam = Camera(WWIDTH,
                        WHEIGHT,
                        WWIDTH/2,
                        WHEIGHT/2, 7.5, 7.5)

        self.fps = Timer()


    def on_load(self):
        for v in self.states.values():
            v.on_load(self.cam, self.font, self.fps)


    def on_reset(self):
        for group in all_groups_list:
            for thing in group:
                thing.kill()


    def on_event(self):
        events = pygame.event.get()
        
        for e in events:
            if e.type == pygame.QUIT:
                self.running = False
            elif e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE:
                    self.running = False
        self.state_curr.on_event(events)


    def on_update(self):
        self.state_curr.on_update()


    def on_render(self):
        self.state_curr.on_render()
        

    def on_execute(self):
        self.on_load()
        while (self.running == True):
            self.fps.on_update()
            self.on_event()
            self.on_update()
            self.on_render()
            
            if self.state_curr.running == False:
                    self.state_curr = self.states[self.state_curr.change_state]
                    self.state_curr.on_resume()
                    continue
            else:
                self.surf_main.blit(self.state_curr.surf_main, (0, 0))
            pygame.display.update()



if __name__ == '__main__':
    random.seed()
    game = Game();
    game.on_execute();
