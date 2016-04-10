#!/usr/bin/env python
import pygame as pg
import random

from constants import WIN_SIZE, CAPTION
from scene import Scene


class Game(object):
    def __init__(self):
        super(Game, self).__init__()

        pg.init()
        self.surf_main = pg.display.set_mode(WIN_SIZE)
        pg.display.set_caption(CAPTION)
        self.debug = False
        self.running = True

        self.scenes = {"scene1": Scene()}
        self.curr_scene = self.scenes["scene1"]

    def on_load(self):
        self.curr_scene.on_load()

    def on_reset(self):
        self.curr_scene.on_reset()

    def on_event(self):
        events = pg.event.get()

        for e in events:
            if e.type == pg.QUIT:
                self.running = False
            elif e.type == pg.KEYDOWN:
                if e.key == pg.K_ESCAPE:
                    self.running = False

        self.curr_scene.on_event(events)

    def on_update(self):
        self.curr_scene.on_update()

    def on_render(self):
        self.curr_scene.on_render()

    def on_execute(self):
        self.on_load()
        while self.running:
            self.on_event()
            self.on_update()
            self.on_render()

            pg.display.update()
            self.surf_main.fill((80, 80, 100, 255))


if __name__ == '__main__':
    random.seed()
    Game().on_execute();
