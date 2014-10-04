import pygame

from pygame.font import Font

from constants import WIN_WIDTH, FONT_DIR, SCALE
from entities  import Entity, StaticText, DynamicText, SewerMan

class System(object):

    def __init__(self):
        super(System, self).__init__()
        
        self.registered_entities = []
    
    def register(self, obj):
        self.registered_entities.append(obj)
        obj.systems.append(self)
    
    def unregister(self, obj):
        self.registered_entities = [
                ent for ent in self.registered_entities
                        if ent != obj]
        
    def global_kill(self, obj):
        for sys in obj.systems:
            sys.unregister(obj)
    
    def update(self, speed_factor):
        pass


class TextSystem(System):

    def __init__(self, font_filename):
        super(TextSystem, self).__init__()

        self.font = Font(FONT_DIR + font_filename, 14)
    
        
    def on_update(self, speed_factor):
        for entity in self.registered_entities:
            if type(entity) == StaticText and entity.loaded == False:
                render_cmp = entity.get_component("rendercomponent")
                geo_cmp = entity.get_component("geometrycomponent")
                
                entity.loaded = True
                render_cmp.image = self.font.render(entity.text, 
                        False, entity.color)
                
                geo_cmp.src_rect.w = render_cmp.image.get_width()
                geo_cmp.src_rect.h = render_cmp.image.get_height()
                
            elif type(entity) == DynamicText:
                render_cmp = entity.get_component("rendercomponent")
                geo_cmp = entity.get_component("geometrycomponent")
                
                render_cmp.image = self.font.render(
                        entity.pretext + str(entity.attr_to_watch) +
                                entity.posttext, 
                        False, entity.color)
                
                geo_cmp.src_rect.w = render_cmp.image.get_width()
                geo_cmp.src_rect.h = render_cmp.image.get_height()
    
    def scale_font(self, render_cmp, geo_cmp):
        image_w = render_cmp.image.get_width()
        image_h = render_cmp.image.get_height()
        
        render_cmp.image = pygame.transform.scale(render_cmp.image, 
                (image_w * SCALE,
                 image_h * SCALE))
                 

class FpsTextSystem(TextSystem):

    def __init__(self, font_filename, fps_object):
        super(FpsTextSystem, self).__init__(font_filename)

        self.fps = fps_object
    
    
    def on_update(self, speed_factor):
        for entity in self.registered_entities:
            render_cmp = entity.get_component("rendercomponent")
            geo_cmp    = entity.get_component("geometrycomponent")
            
            render_cmp.image = self.font.render("FPS: " + str(self.fps.frames) + "/s",
                    False, (0,0,255))
            geo_cmp.src_rect.w = render_cmp.image.get_width()
            geo_cmp.src_rect.h = render_cmp.image.get_height()
            
        
class AnimationSystem(System):

    def __init__(self):
        super(AnimationSystem, self).__init__()

    def on_update(self, speed_factor):
        for entity in self.registered_entities:
            anim_cmp = entity.get_component("animationcomponent")
            geo_cmp  = entity.get_component("geometrycomponent")
            if anim_cmp == None:
                print str(entity) + "Has No Animation Component"
            if geo_cmp == None:
                print str(entity) + "Has No Geometry Component"
            self.on_animate(anim_cmp)
            self.set_subsurface(geo_cmp, anim_cmp.curr_frame)
            
    def set_subsurface(self, geo_cmp, curr_frame):
        geo_cmp.src_rect.x = geo_cmp.dst_rect.w * curr_frame
            
    def on_animate(self, anim_cmp):
        anim_cmp.new_time = pygame.time.get_ticks()
        
        if anim_cmp.new_time > anim_cmp.last_time + anim_cmp.rate:
            anim_cmp.last_time = anim_cmp.new_time

            anim_cmp.next_frame += 1

            if anim_cmp.next_frame >= len(anim_cmp.curr_sequence):
                anim_cmp.next_frame = 0;

            anim_cmp.curr_frame = anim_cmp.curr_sequence[anim_cmp.next_frame]
            
        
class MovementSystem(System):

    def __init__(self):
        super(MovementSystem, self).__init__()
    
    def on_update(self, speed_factor):
        for entity in self.registered_entities:
            
            geo_cmp = entity.get_component("geometrycomponent")
            physics_cmp = entity.get_component("physicscomponent")
            if physics_cmp == None:
                print str(entity) + "Has No Physics Component"
            if geo_cmp == None:
                print str(entity) + "Has No Geometry Component"
            geo_cmp.position += physics_cmp.velocity * speed_factor
            geo_cmp.dst_rect.x, geo_cmp.dst_rect.y = geo_cmp.position


class EventSystem(System):

    def __init__(self):
        super(EventSystem, self).__init__()
        
    def on_update(self, speed_factor):
        pass
    
    def notify(self, entity, event):
        for entity in self.registered_entities:
            entity.on_notify(entity, event)


class CameraSystem(System):

    def __init__(self):
        super(CameraSystem, self).__init__()

    def on_update(self, speed_factor):
        pass


class CollisionDetectionSystem(System):

    def __init__(self):
        super(CollisionDetectionSystem, self).__init__()
        self.minimum_search_area = pygame.Rect(0, 0, 256, 256) 
        self.debug = False
        surf_main = pygame.display.get_surface()
        self.surf  = pygame.Surface((surf_main.get_width(), surf_main.get_height()))
        self.surf.convert_alpha()
    
    def show_boxes(self):
        self.debug = True
    
    def search_area(self, test_list, (low_x, high_x), (low_y, high_y)):
        entities_in_quadrant = []
        ret_list             = []
        
        quadrant_r = pygame.Rect(low_x, low_y, high_x - low_x, high_y - low_y)
        quadrant_size = pygame.Rect(0, 0, high_x - low_x, high_y - low_y)
        
        #print quadrant_r
            
        for entity in test_list:
            geo_cmp = entity.get_component("geometrycomponent")
            if geo_cmp.dst_rect.colliderect(quadrant_r):
                entities_in_quadrant.append(entity)
        
        if len(entities_in_quadrant) <= 1:
            return [entities_in_quadrant]
            
        if (self.minimum_search_area.contains(quadrant_size)):
            return [entities_in_quadrant]
        
        div_line_x = (quadrant_r.w / 2) + quadrant_r.x
        div_line_y = (quadrant_r.h / 2) + quadrant_r.y
        
        quad1 = self.search_area(entities_in_quadrant, 
                (low_x, div_line_x),(low_y, div_line_y))
        quad2 = self.search_area(entities_in_quadrant,
                (low_x, div_line_x),(div_line_y, high_y))
        quad3 = self.search_area(entities_in_quadrant,
                (div_line_x, high_x),(low_y, div_line_y))     
        quad4 = self.search_area(entities_in_quadrant,
                (div_line_x, high_x),(div_line_y, high_y))
                
        if self.debug == True:
            self.surf.fill((0, 0, 0, 0))
            pygame.draw.rect(self.surf, (0, 255, 0, 128), quadrant_r, 1)
            [pygame.draw.rect(self.surf, (255, 0, 0, 128), swrmn.get_component("geometrycomponent").dst_rect, 1)
                    for swrmn in entities_in_quadrant if isinstance(swrmn, SewerMan)]
        
        for quad in [quad1, quad2, quad3, quad4]:
            if len(quad) > 0:
                    ret_list = ret_list + quad
                    
        return ret_list

    def on_update(self, speed_factor):
        largest_x   = max(self.registered_entities, key=lambda ent: 
                ent.get_component("geometrycomponent").dst_rect.right).get_component("geometrycomponent").dst_rect.right
        largest_y   = max(self.registered_entities, key=lambda ent: 
                ent.get_component("geometrycomponent").dst_rect.bottom).get_component("geometrycomponent").dst_rect.bottom
        smallest_x  = min(self.registered_entities, key=lambda ent:
                ent.get_component("geometrycomponent").position.x).get_component("geometrycomponent").position.x
        smallest_y  = min(self.registered_entities, key=lambda ent: 
                ent.get_component("geometrycomponent").position.y).get_component("geometrycomponent").position.y
        
        list_to_test = self.search_area(self.registered_entities, 
                (smallest_x, largest_x), (smallest_y, largest_y))
                
        count = 0
        for _list in list_to_test:
            for ent1 in _list:
                for ent2 in _list:
                    if ent1 == ent2:
                        continue
                    count += 1
                    if ent1.get_component("geometrycomponent").dst_rect.colliderect(
                            ent2.get_component("geometrycomponent").dst_rect):
                        ent1.on_notify(ent2, "collision")
                        ent2.on_notify(ent1, "collision")
        
        print "Ran " + str(count) + " tests using " + str(len(list_to_test)) + " groups"
                        
        
    
class RenderSystem(System):

    def __init__(self):
        super(RenderSystem, self).__init__()
        self.surf_main = pygame.display.get_surface()
        
        
    def on_update(self, speed_factor):
        for entity in self.registered_entities:
            render_cmp = entity.get_component("rendercomponent")
            geo_cmp    = entity.get_component("geometrycomponent")
            
            if geo_cmp == None:
                print str(entity) + "Has No Geometry Component"
            if render_cmp == None:
                print str(entity) + "Has No Render Component"
            
            self.surf_main.blit(render_cmp.image, geo_cmp.dst_rect, 
                    geo_cmp.src_rect)
