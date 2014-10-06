import pygame

from components import *

class Entity(object):

    def __init__(self, collidable):
        super(Entity, self).__init__()
        
        self.collidable = True
        self.components = []
        self.systems    = []
    
    def get_component(self, component_type):
        """ Iterate through component list for a component with
            the matching String """
        return next((comp for comp in self.components 
                if comp.component_type == component_type), 
            None)
    
    def on_notify(self, entity, event):
        pass
        

class Text(Entity):

    def __init__(self, position, color):
        super(Text, self).__init__(False)
        
        self.loaded = False
        self.color = color
        self.components.append(GeometryComponent(self, position))
        self.components.append(RenderComponent(self))


class StaticText(Text):

    def __init__(self, the_text, position, color):
        super(StaticText, self).__init__(position, color)

        self.text  = the_text
        
    

class DynamicText(Text):
    """ The image for this class is created
        only by the TextSystem it is registered to """
    def __init__(self, pretext, attr_to_watch, posttext, position, color):
        super(DynamicText, self).__init__(position, color)

        self.pretext = pretext
        self.attr_to_watch = attr_to_watch
        self.posttext = posttext
        

class Camera(Entity):

    def __init__(self, ww, wh, offx, offy, vx, vy):
        super(Camera, self).__init__(False)
        self.components.append(GeometryComponent(self, (0,0), (ww, wh)))
      
        self.target     = None
        
        self.offset     = Vector(offx, offy)
        self.velocity   = Vector(vx, vy)
        
        self.elapsed    = 0
        self.sinspeedx  = .05
        self.sinspeedy  = .10

    def follow(self, target):
        self.target     = target

    
class Bullet(Entity):

    def __init__(self, x, y, direction=(1, 0)):
        super(Bullet, self).__init__(True)
        
        self.speed = 3
        
        self.components.append(PhysicsComponent(self, 
                (direction[0] * self.speed, direction[1] * self.speed),
                (10, 10),
                (0, 0)))
        self.components.append(GeometryComponent(self, (x, y), (10, 10)))
        self.components.append(RenderComponent(self))


class Tile(Entity):
    
    def __init__(self, image_filename, position=(0,0), dimensions=(10,10), 
            sub_surf=(0,0)):
        super(Tile, self).__init__(True)
        
        self.components.append(GeometryComponent(self, position, dimensions, 
                        sub_surf))
        self.components.append(RenderComponent(self, image_filename)) 
        

class SewerMan(Entity):

    def __init__(self, position=(0,0)):
        super(SewerMan, self).__init__(True)
        
        self.face_left = False
        anim_cmp = AnimationComponent(self, 7.5)
        
        anim_cmp.sequences["walk"]  = [1, 2, 1, 3, 4, 3,]
        anim_cmp.sequences["stand"] = [0]
        anim_cmp.sequences["jump"]  = [2]
        anim_cmp.curr_sequence = anim_cmp.sequences["walk"]
        
        self.components.append(anim_cmp)
        self.components.append(PhysicsComponent(self, (12, 0), (10, 10), (0,0)))
        self.components.append(MovementComponent(self, position))
        self.components.append(GeometryComponent(self, position, (10,10)))
        self.components.append(RenderComponent(self, 'SewerMan.png'))
    
    def on_notify(self, entity, event):
        if event == "collision":
            #print "Collision: ", self, entity
            phy_cmp = self.get_component("physicscomponent")
            geo_cmp = self.get_component("geometrycomponent")
            phy_cmp.velocity.x *= -1
            geo_cmp.position.x += phy_cmp.velocity.x
            geo_cmp.dst_rect.x, geo_cmp.dst_rect.y = geo_cmp.position
            
