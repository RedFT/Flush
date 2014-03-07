import pygame
import random

from pygame              import Surface, font
 
from state               import State
from data                import *
from constants           import *
from utils               import Timer
from drawables           import *

from retrogamelib.camera import Camera, ParallaxCamera
from retrogamelib.dialog import DialogBox

class PlayState(State):
    def __init__(self):
        super(PlayState, self).__init__()

        self.debug = False
        self.scale = 6

        self.elapsed = 0
        self.sinspeed = random.uniform(.1, .2)

    def on_resume(self):
        super(PlayState, self).on_resume()
        for snow in snowbg_sprites_list:
            snow.set_pos(self.cam.rect)
        for snow in snowfg_sprites_list:
            snow.set_pos(self.cam.rect)
        self.cam.follow(self.controller)

    def on_reset(self):
        for group in all_groups_list:
            for thing in group:
                thing.kill()


    def on_load(self, camera=None, font=None, fps=None):
        super(PlayState, self).on_load(camera, font, fps)
        self.text = self.font.render("DEBUG", 0,  (255, 255, 0, 0))
        self.text_fps = self.font.render("FPS: 0", 0, (255, 255, 0, 0))

        self.dialog = DialogBox((150, 120),
                        (50, 75, 100, 180),
                        (200, 200, 200, 200),
                        self.font, self.scale)
        self.dialog.set_dialog(["Hello", "Welcome", "Goodbye"])
        self.dialog.set_scrolldelay(10)
        self.dialog.set_dialog(STORY["intro.txt"])
            
        self.fog = Drawable("Fog.png",
                       x=0, y=0,
                       w=WWIDTH, h=WHEIGHT,
                       resize=None,
                       groups=[all_sprites_list, fog_sprites_list,])

        self.dist = Surface((self.surf_main.get_width(), self.surf_main.get_height())).convert_alpha()
        self.dist.fill((12, 12, 22, 200))

        load_map("tallmap.tmx", "bg", self.scale/ 2, False,    [tilebg_sprites_list])
        load_map("tallmap.tmx", "mg", self.scale, True,        [tilemg_sprites_list])
        load_map("tallmap.tmx", "fg", self.scale, False,   [tilefg_sprites_list])
        
        snow_bg  = SnowFallBG (10, self.scale / self.scale, [all_sprites_list, snowbg_sprites_list])
        snow_fg  = SnowFallBG (5, self.scale / 2,           [all_sprites_list, snowfg_sprites_list])

        self.player = Player("SewerMan2.png", 
                             x=300, y=50, 
                             w=10, h=11, 
                             resize=self.scale, 
                             groups=[all_sprites_list, player_sprites_list])

        self.entity = Player("SewerMan.png", 
                             x=400, y=50,
                             w=10, h=11, 
                             resize=self.scale, 
                             groups=[all_sprites_list, enemy_sprites_list])

        self.controller = self.player

        self.cam.follow(self.player)
        self.cam.x = self.player.x
        self.cam.y = self.player.y


    def on_event(self, e):
        for event in e:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:
                    self.running = False
                    self.change_state = "pausestate"

                elif event.key == pygame.K_RETURN:
                    pass

                elif event.key == pygame.K_r:
                    self.on_reset()
                    self.on_load()

                elif event.key == pygame.K_5:
                    pass
                    if self.controller == self.player:
                        self.controller = self.entity
                    else:
                        self.controller = self.player
                    self.cam.follow(self.controller)

                elif event.key == pygame.K_LEFT:
                    self.controller.move_left = True

                elif event.key == pygame.K_RIGHT:
                    self.controller.move_right = True

                elif event.key == pygame.K_UP:
                    if self.controller.can_jump:
                        self.controller.jump = True

                elif event.key == pygame.K_DOWN:
                    pass

                elif event.key == pygame.K_SLASH:
                    self.controller.super_jump()

                elif event.key == pygame.K_RSHIFT:
                    self.controller.shoot()

                elif event.key == pygame.K_d:
                    self.debug = not self.debug

                elif event.key == pygame.K_SPACE:
                    self.dialog.progress()

            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_LEFT:
                    self.controller.move_left = False

                elif event.key == pygame.K_RIGHT:
                    self.controller.move_right = False


    def on_update(self):
        
        self.text_fps = self.font.render("FPS: " + str(self.fps.frames), 0, (255, 255, 0, 0))

        self.elapsed += 1 * self.fps.speed_factor

        for sprite in all_sprites_list:
            sprite.on_update(self.fps.speed_factor)

        self.on_collision()
        self.on_animate()
        self.cam.on_update(self.fps.speed_factor)
        self.paracam.on_update(self.fps.speed_factor)

        for group in all_groups_list:
            if group == all_sprites_list:
                continue
            if group == tilebg_sprites_list or \
               group == snowbg_sprites_list or \
               group == fog_sprites_list:
                self.paracam.translate(group)
            else:
                self.cam.translate(group)

        for snow in snowbg_sprites_list:
            snow.check_collision(self.paracam.rect)
        for snow in snowfg_sprites_list:
            snow.check_collision(self.cam.rect)


    def on_collision(self):
        self.player.on_collide(tilemg_sprites_list)
        for enemy in enemy_sprites_list:
            enemy.on_collide(tilemg_sprites_list)
        for bullet in bullet_sprites_list:
            bullet.on_collide(enemy_sprites_list)
            bullet.on_collide(tilemg_sprites_list)
            bullet.on_collide(bullet_sprites_list)
            bullet.on_collide(player_sprites_list)


    def on_animate(self):
        for enemy in enemy_sprites_list:
            enemy.on_animate()
        self.player.on_animate()


    def on_render(self):
        self.surf_main.fill((14, 50, 75, 0))
        
        for tile in tilebg_sprites_list:
            if self.cam.viewport.colliderect(tile.rect):
                tile.on_render(self.surf_main)

        for snow in snowbg_sprites_list:
            if self.cam.viewport.colliderect(snow.rect):
                snow.on_render(self.surf_main)

        self.surf_main.blit(self.dist, (0, 0))

        for group in all_groups_list:
            if group is all_sprites_list or \
               group is tilebg_sprites_list or \
               group is snowbg_sprites_list:
                continue
            for i in self.cam.viewport.collidelistall(group):
                group[i].on_render(self.surf_main)

        for fog in fog_sprites_list:
            fog.on_render(self.surf_main)
        
        if self.debug: # Draw Boxes and Debug Text
            for sprite in self.cam.viewport.collidelistall(all_sprites_list):
                all_sprites_list[sprite].draw_box(self.surf_main)
            self.cam.draw_box(self.surf_main)
            self.paracam.draw_box(self.surf_main)
            self.cam.draw_box_rect(self.surf_main)
            self.paracam.draw_box_rect(self.surf_main)

            self.surf_main.blit(self.text, (50, 50))
            self.surf_main.blit(self.text_fps, (150, 50))

        if not self.dialog.over():
            y = (1 * (sin(self.elapsed * self.sinspeed) * 4) + self.controller.rect.y)
            self.dialog.draw(self.surf_main,
                    ((self.controller.rect.x +self.controller.rect.w / 2)- self.dialog.width / 2, y - 50))
