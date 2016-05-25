from utils import Timer
import pygame as pg


class Scene(object):
    def __init__(self, ):
        super(Scene, self).__init__()

        self.fps = Timer()
        self.surf_main = pg.display.get_surface()

        self.running = False
        self.loaded = False

        self.last_time = 0

    def is_running(self):
        return self.running

    def is_loaded(self):
        return self.loaded

    def on_load(self):
        self.loaded = True

    def on_reset(self):
        pass

    def on_event(self, events):
        pass

    def on_update(self):
        self.fps.on_update()
        # speed_factor = self.fps.speed_factor

    def on_render(self):
        pass

    def on_run(self):
        self.on_event()
        self.on_update()
        self.on_render()
