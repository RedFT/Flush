import pygame

from systems                 import *
from entities                import *
from components              import *
from utils                   import Timer

from map                     import load_map

from constants               import WIN_SIZE


class Scene(object):

    def __init__(self,):
        super(Scene, self).__init__()
        
        self.fps     = Timer()
        self.surf_main = pygame.display.get_surface()
        
        self.render_sys     = RenderSystem()
        self.move_sys       = MovementSystem()
        self.anim_sys       = AnimationSystem()
        self.fps_text_sys   = FpsTextSystem("Terminus.ttf", self.fps)
        self.collision_sys  = CollisionDetectionSystem()
        #self.collision_sys.show_boxes()
        # Test Map
        tiles_list = load_map("tallmap.tmx", "mg")
        for tile in tiles_list:
            self.render_sys.register(tile)
            if tile.collidable == True:
                self.collision_sys.register(tile)
            
        # Test Player
        self.player     = SewerMan((40, 40))
        self.render_sys.register(self.player)
        self.anim_sys.register(self.player)
        self.move_sys.register(self.player)
        self.collision_sys.register(self.player)
        
        # Test Fps Text
        self.fps_text    = Text((5,5), (0,0,255))
        self.render_sys.register(self.fps_text)
        self.fps_text_sys.register(self.fps_text)
        
        self.running = False
        self.loaded  = False
        
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
        speed_factor = self.fps.speed_factor

        self.fps_text_sys.on_update(speed_factor)
        
        self.move_sys.on_update(speed_factor)
        self.collision_sys.on_update(speed_factor)
        
        self.anim_sys.on_update(speed_factor)
        
    def on_render(self):
        self.render_sys.on_update(self.fps.speed_factor)
        #self.surf_main.blit(self.collision_sys.surf, (0,0))
        pass
    
    def on_run(self):
        self.on_event()
        self.on_update()
        self.on_render()
