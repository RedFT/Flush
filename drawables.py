import random
import pygame

from constants               import *
from retrogamelib.gameobject import *
from retrogamelib.geometry   import *
from retrogamelib.util       import *
from utils                   import Animator, Timer
from math                    import sin


class Drawable(Object):
    def __init__(self, image=None, x=0, y=0, w=16, h=16, resize=None, groups=[], color=(150, 150, 200, 128)):
        super(Drawable, self).__init__(groups)

        self.collidable = True
        
        if image:
            self.image = load_image(IMAGE_DIR + image)
        else:
            self.image = pygame.Surface((w, h)).convert_alpha()
            self.image.fill(color)
            
        self.x = x
        self.y = y
        self.w = w
        self.h = h

        if resize != None:
            self.w = w * resize
            self.h = h * resize
            self.image = pygame.transform.scale(
                self.image, 
                (self.image.get_width() * resize, self.image.get_height() * resize))

        self.rect = pygame.Rect(self.x, self.y, 
                                self.w, self.h)

        self.part = pygame.Rect(0 , 0, 
                                self.w, self.h)

        self.pos = Vector(self.x, self.y)
        self.last_pos = Vector(self.x, self.y)

    def collide_left(self, other):
        if int(self.last_pos[0] + self.w) <= other.x and \
            int(self.pos[0] + self.w) > other.x:
            return True
        return False

    def collide_right(self, other):
        if int(self.last_pos[0]) >= other.x + other.w and \
            int(self.pos[0]) <= other.x + other.w:
            return True
        return False

    def collide_top(self, other):
        if int(self.last_pos[1] + self.h) <= other.y and \
            int(self.pos[1] + self.h) >= other.y:
            return True
        return False

    def collide_bottom(self, other):
        if int(self.last_pos[1]) >= other.y + other.h and \
            int(self.pos[1]) <= other.y + other.h:
            return True
        return False

    def on_collide(self, list):
        pass

    def draw_box(self, surface):
        pygame.draw.lines(surface, (200, 200, 200), True, [(self.rect.x, self.rect.y),
                                                     (self.rect.x, self.rect.bottom),
                                                     (self.rect.right, self.rect.bottom),
                                                     (self.rect.right, self.rect.y)])


    def on_update(self, speed_factor):
        self.rect.x = self.x
        self.rect.y = self.y


    def on_render(self, surface):
        surface.blit(self.image, self.rect, self.part)


class Bullet(Drawable):
    def __init__(self, x, y, w, h, groups, resize=1, face_left=False):
        self.x = x + w
        self.x = (x + w ) + resize
        self.y =  y + (h / 2) + (resize)
        if face_left == True:
            self.x = x - (2 * resize)
                
        self.w = 2 * resize
        
        self.accelx = -.02
        self.accely = .2
        self.vx = 10
        
        if face_left == True:
            self.accelx = .01
            self.vx = -10
            
        self.leastx = .5
        self.maxy   = 5
        self.vy = 0
        
        self.cchange_range = (110, 200)
        self.cchange_speed = 5
        self.color = [179, 120, 75, 255]

        super(Bullet, self).__init__(x=self.x, y=self.y, w=self.w, h=self.w, resize=None, groups=groups, color=self.color)

    def on_collide(self, other):
        for obj in other:
            if obj is self:
                continue
            if not obj.collidable:
                continue
            if self.rect.colliderect(obj.rect):
                self.kill()
                obj.kill()

    def change_color(self, sf):
        if self.cchange_range[0] > self.color[0] or self.color[0] > self.cchange_range[1]:
            self.cchange_speed *= -1
            if self.cchange_range[0] > self.color[0]:
                self.color[0] += 1
            if self.cchange_range[1] < self.color[0]:
                self.color[0] -= 1
            
        self.color[0] += self.cchange_speed * sf
        self.color[1] += self.cchange_speed * sf
        self.image.fill(self.color)
            
            
        
            
    def on_update(self, speed_factor):
        self.change_color(speed_factor)
        """
        self.vx += self.accelx * speed_factor
        self.vy += self.accely * speed_factor
        """
        
        if 0 < self.vx < self.leastx:
            self.vx = 0
        if 0 > self.vx > -self.leastx:
            self.vx = 0
            
        if self.vy > self.maxy:
            self.vy = self.maxy
        if self.vy < -self.maxy:
            self.vy = -self.maxy
            
        self.y += self.vy * speed_factor
        self.x += self.vx * speed_factor
        self.rect.x = self.x
        self.rect.y = self.y
        
        

    def on_render(self, surface):
        surface.blit(self.image, self.rect)
                

class Tile(Drawable):
    def __init__(self, image=None, x=0, y=0, w=16, h=16, tx=0, ty=0, resize=None, groups=[]):
        super(Tile, self).__init__(image, x, y, w, h, resize, groups)

        self.rect.x = x * self.w
        self.rect.y = y * self.h
        self.x = x * self.w
        self.y = y * self.h
        self.tx = tx * self.w
        self.ty = ty * self.h
        self.part = pygame.Rect(self.tx , self.ty, 
                                self.w, self.h)
        


    def on_update(self, speed_factor):
        super(Tile, self).on_update(speed_factor)



class Snow(Drawable):
    def __init__(self, resize=None, groups=[]):
        self.x = random.randint(0, WWIDTH)
        self.y = random.randint(0, WHEIGHT)
        self.w = 1
        self.vx = random.uniform(0, .4) #* random.choice([-1, 1])
        self.vy = random.uniform(-0.2, -.4)
        self.elapsed = 0
        self.sinspeed = random.uniform(.01, .02)
        if resize:
            self.w *= resize
            self.vx *= resize
            self.vy *= resize
        
        super(Snow, self).__init__(x=self.x, y=self.y, w=self.w, h=self.w, groups=groups)


    def set_pos(self, pos_rect):
        self.x = random.randint(pos_rect.x, pos_rect.x + pos_rect.w)
        self.y = random.randint(pos_rect.y, pos_rect.y + pos_rect.h)
        self.rect.x = self.x
        self.rect.y = self.y

    def on_update(self, speed_factor):

        self.last_pos = (self.x, self.y)

        self.x += self.vx * speed_factor
        self.y += self.vy * speed_factor

        self.elapsed += 1 * speed_factor

        self.x = (.25 * (sin(self.elapsed * self.sinspeed) * speed_factor) + self.x)
        
        self.rect.x = self.x
        self.rect.y = self.y

    def on_collide(self, list):
        for obj in list:
            if not obj.collidable:
                continue
            if obj.rect.colliderect(self.rect):
                if (self.collide_top(obj)):
                    self.y = obj.y - self.h - 1
                    self.rect.y = obj.y - self.h - 1
                    self.vy *= -1
                if self.collide_bottom(obj):
                    self.y = obj.y + obj.h + 1
                    self.rect.y = obj.y + obj.h + 1
                    self.vy *= -1
            if obj.rect.colliderect(self.rect):
                if self.collide_left(obj):
                    self.x = obj.x - self.w - 1
                    self.rect.x = obj.x - self.w - 1
                    self.vx *= -1
                if self.collide_right(obj):
                    self.x = obj.x + obj.w + 1
                    self.rect.x = obj.x + obj.w + 1
                    self.vx *= -1

    def check_collision(self, viewport):
        if self.x > viewport.x + viewport.w + self.w:
            self.x = viewport.x - self.w
        
        if self.y > viewport.y + viewport.h  + self.w:
            self.y = viewport.y - self.w

        if self.x < viewport.x - self.w:
            self.x = viewport.x + viewport.w + self.w

        if self.y < viewport.y - self.w:
            self.y = viewport.y + viewport.h + self.w

    def on_render(self, surface):
        surface.blit(self.image, self.rect)
        self.draw_box(surface)
        

class SnowFallBG(object):

    def __init__(self, num_snow=30, resize=None, groups=[]):
        super(SnowFallBG, self).__init__()

        for i in range(num_snow):
            snow = Snow(resize, groups)


class Entity(Drawable):

    def __init__(self, image, x=0, y=0, w=16, h=16, resize=None, groups=[]):
        super(Entity, self).__init__(image, x, y, w, h, resize, groups)

        self.resize = resize

        self.move_left      = False
        self.move_right     = False
        self.face_left      = False
        self.jump           = False
        self.front_jump     = True
        self.can_jump       = True
        self.still          = False
        self.slowing        = True
        self.on_ground      = False
        self.super_jumping  = False

        self.super_jump_count = 10

        self.vx             = 0.
        self.vy             = 0.

        self.accelx         = 1.
        self.accely         = 1

        self.maxx           = 15
        self.maxy           = 11

        self.walk_sequence  = [
            1, 2, 1, 3, 4, 3,
        ]
        self.anim           = Animator(100)
        

    def super_jump(self):
        
        if self.on_ground and self.super_jump_count > 0:
            self.vy         = -self.maxy * 1.25
            self.super_jumping = True
            self.on_ground  = False
            self.jump       = False
            self.front_jump = not self.front_jump
            self.super_jump_count -= 1

    def on_collide(self, list):
        for obj in list:
            if not obj.collidable:
                continue
            if obj.rect.colliderect(self.rect):
                if (self.collide_top(obj)):
                    self.y = obj.y - (self.h)
                    self.rect.y = obj.y - (self.h)
                    self.on_ground = True
                    self.super_jumping = False
                    if isinstance(obj, Entity) or isinstance(obj, Player):
                        self.vy *= -.25
                    else:
                        self.vy = 0
                if self.collide_bottom(obj):
                    self.y = obj.y + (obj.h - 1)
                    self.rect.y = obj.y + (obj.h - 1)
                    self.vy *= -.25
            if obj.rect.colliderect(self.rect):
                if self.collide_left(obj):
                    self.x = obj.x - (self.w + 1)
                    self.rect.x = obj.x - (self.w + 1)
                    self.vx *= -.25
                if self.collide_right(obj):
                    self.x = obj.x + (obj.w + 1)
                    self.rect.x = obj.x + (obj.w + 1)
                    self.vx *= -.25

    def on_update(self, speed_factor):
        self.slowing = True
        if not self.move_left and not self.move_right:
            if self.vx > 0:
                self.accelx = -.5

            elif self.vx < 0:
                self.accelx = .5

            elif self.vy < 0:
                self.accely = .25

            if -self.accelx < self.vx < self.accelx:
                self.vx = 0
                self.accelx = 0
                self.slowing = False
                self.still = True

        if self.move_left:
            self.slowing = False
            self.still = False
            self.face_left = True
            self.accelx = -.25

        elif self.move_right:
            self.slowing = False
            self.still = False
            self.face_left = False
            self.accelx = .25

        if self.jump and self.on_ground:
            self.vy         = -self.maxy / 2
            self.on_ground  = False
            self.jump       = False
            self.front_jump = not self.front_jump


        if self.vx > self.maxx: 
            self.vx = self.maxx
        if self.vx < -self.maxx: 
            self.vx = -self.maxx

        if self.vy > self.maxy: 
            self.vy = self.maxy
                
        if not self.super_jumping:
            if self.vy < -self.maxy: 
                self.vy = -self.maxy
        else:
            if self.vy < -self.maxy * 2: 
                self.vy = -self.maxy * 2

        self.vx += self.accelx * speed_factor
        self.vy += self.accely * speed_factor

        self.last_pos = (self.x, self.y)

        self.x += self.vx * speed_factor
        self.y += self.vy * speed_factor
        self.rect.x = self.x
        self.rect.y = self.y

        self.pos = (self.x, self.y)

        if self.vx != 0:
            self.anim.rate = 850 / abs(self.vx)
            if self.anim.rate > 200:
                self.anim.rate - 100
        self.anim.on_update(self.walk_sequence)
        
    def on_animate(self):
        if not self.on_ground:
            self.can_jump = False
        else:
            self.can_jump = True
        if self.pos[1] - self.last_pos[1] > .8:
            self.on_ground = False
        elif not self.on_ground:
            self.part.x = self.part.w * 2
            self.anim.next_frame = 5
        elif self.still:
            self.part.x = 0
            self.anim.next_frame = 5
        elif self.slowing:
            self.part.x = self.part.w
            self.anim.next_frame = 5
        else:
            self.part.x = self.part.w * self.anim.current_frame


    def shoot(self):
        bullet = Bullet(self.x, self.y, self.w, self.h, groups=[all_sprites_list, bullet_sprites_list],
                        resize=self.resize, face_left=self.face_left)
 


    def on_render(self, surface):
        if self.face_left:
            sub = self.image.subsurface(self.part)
            sub = pygame.transform.flip(sub, True, False)
            surface.blit(sub, self.rect)
        else:
            surface.blit(self.image, self.rect, self.part)


class Player(Entity):
    def __init__(self, image, x=0, y=0, w=16, h=16, resize=None, groups=[]):
        super(Player, self).__init__(image, x, y, w, h, resize, groups)
