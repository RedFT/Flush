import pygame

from constants              import IMAGE_DIR, SCALE
from utils                  import load_image
from retrogamelib.geometry  import Vector


class Component(object):

    def __init__(self, owner, component_type="component"):
        super(Component, self).__init__()
        self.owner          = owner
        self.component_type = component_type


class AnimationComponent(Component):
    def __init__(self, owner, rate):
        super(AnimationComponent, self).__init__(owner, "animationcomponent")

        self.rate = 1000. / rate # the fps to animate at

        self.new_time = 0
        self.last_time = 0
        self.diff_time = 0

        self.next_frame = 0
        self.curr_frame = 0
        
        self.sequences = {}     # dictionary of animation sequences
        self.curr_sequence = [] # the current animation sequence
    
    def new_sequence(self, new_sequence_name, new_sequence):
        self.sequences[new_sequence_name] = new_sequence
    
    def set_current_sequence(self, sequence_name):
        self.curr_sequence = self.sequences[sequence_name]


class PhysicsComponent(Component):

    def __init__(self, owner, 
            velocity=(0, 0), 
            maximum_velocity=(0, 0), 
            initial_acceleration=(0, 0)):
        super(PhysicsComponent, self).__init__(owner, "physicscomponent")
        
        self.velocity       = Vector(*velocity)
        self.velocity_max   = Vector(*maximum_velocity)
        self.acceleration   = Vector(*initial_acceleration)

        
class GeometryComponent(Component):

    def __init__(self, owner, position=(0, 0), dimensions=(10, 10), subsurf=None):
        super(GeometryComponent, self).__init__(owner, "geometrycomponent")
        
        # Scale each argument passed in, by the constant SCALE
        scaled_position   = tuple(i * SCALE for i in position)
        scaled_dimensions = tuple(i * SCALE for i in dimensions)
        if subsurf:
            scaled_subsurface = tuple(i * SCALE for i in subsurf)
            self.src_rect = pygame.Rect(*(scaled_subsurface + scaled_dimensions))
        else:
            self.src_rect = pygame.Rect(0, 0, *scaled_dimensions)
            
            
        self.position = Vector(*scaled_position)
        self.dst_rect = pygame.Rect(*(scaled_position + scaled_dimensions))
        

class RenderComponent(Component):

    def __init__(self, owner, image=None, color=(255, 0, 255)):
        super(RenderComponent, self).__init__(owner, "rendercomponent")

        if not image:
            geo_cmp = owner.get_component("geometrycomponent")
            rect = geo_cmp.src_rect
            self.image  = pygame.Surface((rect.w, rect.h)).convert_alpha()
            self.image.fill(color);
            return
        if type(image) == pygame.Surface:
            self.image = image
        else:
            self.image      = load_image(IMAGE_DIR + image)
