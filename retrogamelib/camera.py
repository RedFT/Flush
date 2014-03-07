import pygame

from math import sin
class Camera(object):
    
    def __init__(self, ww, wh, offx, offy, vx, vy):
        self.rect = pygame.Rect(0, 0, ww, wh)
        self.x, self.y = self.rect.x, self.rect.y
        self.target = None
        self.offx = offx
        self.offy = offy
        self.vx = vx
        self.vy = vy
        self.frozen = []  #Objects blocking camera from moving
        self.viewport = pygame.Rect(0, 0, ww, wh)
        self.elapsed = 0
        self.sinspeedx = .05
        self.sinspeedy = .10

    def follow(self, target):
        self.target = target
    
    def on_update(self, speed_factor):
        dx = (float(self.target.x ) - self.x) + (self.target.w / 2)
        dy = (float(self.target.y ) - self.y) + (self.target.h / 2)

        #if abs(dx) > 88:
        vx = dx / self.vx
        self.x += (vx * speed_factor)

        #if abs(dy) > 88:
        vy = dy / self.vy
        self.y += (vy * speed_factor)
        self.elapsed += 1 * speed_factor
        x = (1 * (sin(self.elapsed * self.sinspeedx) * 4) + self.x)
        y = (1 * (sin(self.elapsed * self.sinspeedy) * 4) + self.y)
        self.rect.x = x - self.offx
        self.rect.y = y - self.offy

    def translate(self, group):
        for other in group:
            other.rect.x -= self.rect.x
            other.rect.y -= self.rect.y
        
    def freeze(self, object):
        if object not in self.frozen:
            self.frozen.append(object)
            
    def unfreeze(self, object):
        if object in self.frozen:
            self.frozen.remove(object)
    
    def center_at(self, pos):
        if not self.frozen:
            self.offset = list(pos)
            self.target = None

    def draw_box(self, surface):
        pygame.draw.lines(surface, (0, 0, 0), True, [(self.viewport.x, self.viewport.y),
                                                     (self.viewport.x, self.viewport.bottom),
                                                     (self.viewport.right, self.viewport.bottom),
                                                     (self.viewport.right, self.viewport.y)])

    def draw_box_rect(self, surface):
        pygame.draw.lines(surface, (0, 0, 0), True, [(self.rect.x, self.rect.y),
                                                     (self.rect.x, self.rect.bottom),
                                                     (self.rect.right, self.rect.bottom),
                                                     (self.rect.right, self.rect.y)])


class ParallaxCamera(Camera):
    def __init__(self, camera, x_factor=1, y_factor=1):
        super(ParallaxCamera, self).__init__(camera.rect.w, camera.rect.h,
                                             camera.offx, camera.offy,
                                             camera.vx,   camera.vy)
        self.camera = camera
        self.xf = x_factor
        self.yf = y_factor

    def on_update(self, speed_factor):
        self.rect.x = self.camera.rect.x / self.xf
        self.rect.y = self.camera.rect.y / self.xf

    def translate(self, group):
        for other in group:
            other.rect.x -= self.rect.x
            other.rect.y -= self.rect.y
