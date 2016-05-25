import pygame as pg

from map import load_map
from scenes.scene import Scene
from ecs.systems.systems import RenderSystem, PlayerMovementSystem, PlayerAnimationSystem, FpsTextSystem,\
    CollisionDetectionSystem, EventSystem, CameraSystem
from ecs.entities.entities import SewerMan, Text, Camera, Bullet
from constants import WIN_HEIGHT, WIN_WIDTH


class TestScene1(Scene):
    def __init__(self, ):
        super(TestScene1, self).__init__()

        self.render_sys = RenderSystem()
        self.player_move_sys = PlayerMovementSystem()
        self.player_animation_sys = PlayerAnimationSystem()
        self.fps_text_sys = FpsTextSystem("Terminus.ttf", self.fps)
        self.collision_sys = CollisionDetectionSystem()
        self.event_sys = EventSystem()
        self.camera_sys = CameraSystem()

        # Test Map
        tiles_list = load_map("tallmap.tmx", "mg")
        for tile in tiles_list:
            self.render_sys.register(tile)

            if tile.is_collidable:
                self.collision_sys.register(tile)

            self.camera_sys.register(tile)

        # Test Player
        self.player = SewerMan((40, 40))
        self.render_sys.register(self.player)
        self.player_animation_sys.register(self.player)
        self.player_move_sys.register(self.player)
        self.collision_sys.register(self.player)
        self.event_sys.register(self.player,
                                ["up_pressed", "down_pressed", "left_pressed", "right_pressed",
                                 "up_released", "down_released", "left_released", "right_released"])
        self.camera_sys.register(self.player)

        # multiple entities
        for i in range(6, 6 * 2 + 1, 6):
            player = SewerMan((i * 10, 40))
            self.render_sys.register(player)
            self.player_animation_sys.register(player)
            self.player_move_sys.register(player)
            self.collision_sys.register(player)
            self.camera_sys.register(player)

        # Test Fps Text
        self.fps_text = Text((5, 5), (0, 0, 255))
        self.render_sys.register(self.fps_text)
        self.fps_text_sys.register(self.fps_text)

        self.cam = Camera(
            WIN_WIDTH, WIN_HEIGHT,
            WIN_WIDTH / 2, WIN_HEIGHT / 2,
            7.5, 7.5)
        self.camera_sys.register_camera(self.cam)
        self.render_sys.register_camera(self.cam)
        self.cam.follow(self.player)

    def is_running(self):
        return self.running

    def is_loaded(self):
        return self.loaded

    def on_load(self):
        self.loaded = True

    def on_reset(self):
        pass

    def on_event(self, events):
        for e in events:
            if e.type == pg.KEYDOWN:
                if e.key == pg.K_UP:
                    self.event_sys.notify(None, "up_pressed")
                if e.key == pg.K_DOWN:
                    self.event_sys.notify(None, "down_pressed")
                if e.key == pg.K_LEFT:
                    self.event_sys.notify(None, "left_pressed")
                if e.key == pg.K_RIGHT:
                    self.event_sys.notify(None, "right_pressed")
                if e.key == pg.K_EQUALS:
                    self.event_sys.notify(None, "equals_pressed")
                if e.key == pg.K_MINUS:
                    self.event_sys.notify(None, "minus_pressed")
                if e.key == pg.K_SPACE:
                    self.event_sys.notify(None, "space_pressed")

            if e.type == pg.KEYUP:
                if e.key == pg.K_UP:
                    self.event_sys.notify(None, "up_released")
                if e.key == pg.K_DOWN:
                    self.event_sys.notify(None, "down_released")
                if e.key == pg.K_LEFT:
                    self.event_sys.notify(None, "left_released")
                if e.key == pg.K_RIGHT:
                    self.event_sys.notify(None, "right_released")

    def on_update(self):
        self.fps.on_update()

        speed_factor = self.fps.speed_factor
        self.fps_text_sys.on_update(speed_factor)

        self.player_move_sys.on_update(speed_factor)
        self.collision_sys.on_update(speed_factor)
        self.player_animation_sys.on_update(speed_factor)
        self.camera_sys.on_update(speed_factor)

    def on_render(self):
        self.render_sys.on_update(self.fps.speed_factor)

    def on_run(self):
        self.on_event()
        self.on_update()
        self.on_render()

class TestScene2(Scene):
    def __init__(self, ):
        super(TestScene2, self).__init__()

        self.render_sys = RenderSystem()
        self.player_move_sys = PlayerMovementSystem()
        self.player_animation_sys = PlayerAnimationSystem()
        self.fps_text_sys = FpsTextSystem("Terminus.ttf", self.fps)
        self.collision_sys = CollisionDetectionSystem()
        self.event_sys = EventSystem()
        self.camera_sys = CameraSystem()

        # Test Map
        tiles_list = load_map("stupidmap.tmx", "mg")
        for tile in tiles_list:
            self.render_sys.register(tile)

            if tile.is_collidable:
                self.collision_sys.register(tile)

            self.camera_sys.register(tile)

        # Test Player
        self.player = SewerMan((40, 40))
        self.render_sys.register(self.player)
        self.player_animation_sys.register(self.player)
        self.player_move_sys.register(self.player)
        self.collision_sys.register(self.player)
        self.event_sys.register(self.player,
                                ["up_pressed", "down_pressed", "left_pressed", "right_pressed",
                                 "up_released", "down_released", "left_released", "right_released"])
        self.camera_sys.register(self.player)

        # multiple entities
        for i in range(6, 6 * 2 + 1, 6):
            player = SewerMan((i * 10, 40))
            self.render_sys.register(player)
            self.player_animation_sys.register(player)
            self.player_move_sys.register(player)
            self.collision_sys.register(player)
            self.camera_sys.register(player)

        # Test Fps Text
        self.fps_text =Text((5, 5), (0, 0, 255))
        self.render_sys.register(self.fps_text)
        self.fps_text_sys.register(self.fps_text)

        self.cam = Camera(
            WIN_WIDTH, WIN_HEIGHT,
            WIN_WIDTH / 2, WIN_HEIGHT / 2,
            7.5, 7.5)
        self.camera_sys.register_camera(self.cam)
        self.render_sys.register_camera(self.cam)
        self.cam.follow(self.player)

    def is_running(self):
        return self.running

    def is_loaded(self):
        return self.loaded

    def on_load(self):
        self.loaded = True

    def on_reset(self):
        pass

    def on_event(self, events):
        for e in events:
            if e.type == pg.KEYDOWN:
                if e.key == pg.K_UP:
                    self.event_sys.notify(None, "up_pressed")
                if e.key == pg.K_DOWN:
                    self.event_sys.notify(None, "down_pressed")
                if e.key == pg.K_LEFT:
                    self.event_sys.notify(None, "left_pressed")
                if e.key == pg.K_RIGHT:
                    self.event_sys.notify(None, "right_pressed")
                if e.key == pg.K_EQUALS:
                    self.event_sys.notify(None, "equals_pressed")
                if e.key == pg.K_MINUS:
                    self.event_sys.notify(None, "minus_pressed")
                if e.key == pg.K_SPACE:
                    self.event_sys.notify(None, "space_pressed")

            if e.type == pg.KEYUP:
                if e.key == pg.K_UP:
                    self.event_sys.notify(None, "up_released")
                if e.key == pg.K_DOWN:
                    self.event_sys.notify(None, "down_released")
                if e.key == pg.K_LEFT:
                    self.event_sys.notify(None, "left_released")
                if e.key == pg.K_RIGHT:
                    self.event_sys.notify(None, "right_released")

    def on_update(self):
        self.fps.on_update()

        speed_factor = self.fps.speed_factor
        self.fps_text_sys.on_update(speed_factor)

        self.player_move_sys.on_update(speed_factor)
        self.collision_sys.on_update(speed_factor)
        self.player_animation_sys.on_update(speed_factor)
        self.camera_sys.on_update(speed_factor)

    def on_render(self):
        self.render_sys.on_update(self.fps.speed_factor)

    def on_run(self):
        self.on_event()
        self.on_update()
        self.on_render()
