#!/usr/bin/env python
import pygame as pg
import random

from constants import WIN_SIZE, CAPTION
from scenes.test_scene import TestScene1, TestScene2


class Game(object):
    def __init__(self):
        super(Game, self).__init__()

        pg.init()
        self.surf_main = pg.display.set_mode(WIN_SIZE)
        pg.display.set_caption(CAPTION)
        self.debug = False
        self.running = True

        self.scenes = {
            1: TestScene1(),
            2: TestScene2(),
        }
        self.curr_scene = self.scenes[1]

    def on_load(self):
        if self.curr_scene is not None:
            self.curr_scene.on_load()

    def on_reset(self):
        if self.curr_scene is not None:
            self.curr_scene.on_reset()

    def scene_forward(self):
        for key, value in self.scenes.iteritems():
            if value == self.curr_scene:
                new_key = key + 1
                try:
                    self.curr_scene = self.scenes[new_key]
                except KeyError:
                    return
                print "Loading level: " + str(new_key)
                self.on_reset()
                self.on_load()
                return

    def scene_backward(self):
        for key, value in self.scenes.iteritems():
            if value == self.curr_scene:
                new_key = key - 1
                try:
                    self.curr_scene = self.scenes[new_key]
                except KeyError:
                    return
                print "Loading level: " + str(new_key)
                self.on_reset()
                self.on_load()
                return

    def on_event(self):
        events = pg.event.get()

        for e in events:
            if e.type == pg.QUIT:
                self.running = False
            elif e.type == pg.KEYDOWN:
                if e.key == pg.K_ESCAPE:
                    self.running = False

            elif e.type == pg.KEYUP:
                if e.key == pg.K_TAB and pg.key.get_mods() & pg.KMOD_SHIFT:
                    self.scene_backward()

                elif e.key == pg.K_TAB:
                    self.scene_forward()

        if self.curr_scene is not None:
            self.curr_scene.on_event(events)

    def on_update(self):
        if self.curr_scene is not None:
            self.curr_scene.on_update()

    def on_render(self):
        if self.curr_scene is not None:
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
