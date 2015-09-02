import pygame

from constants import IMAGE_DIR, SCALE
from utils import load_image
from retrogamelib.geometry import Vector


class Component(object):

    def __init__(self, owner, component_type="component"):
        super(Component, self).__init__()
        self.owner = owner
        self.component_type = component_type

    def reload(self):
        pass


class AnimationComponent(Component):

    def __init__(self, owner, rate):
        super(AnimationComponent, self).__init__(owner, "animationcomponent")

        self.rate = 1000. / rate  # the fps to animate at

        self.new_time = 0
        self.last_time = 0
        self.diff_time = 0

        self.next_frame = 0
        self.curr_frame = 0

        self.sequences = {}     # dictionary of animation sequences
        self.curr_sequence = []  # the current animation sequence

    def __len__(self):
        len(self.sequences.keys())

    def __setitem__(self, key, item):
        self.sequences[key] = item

    def __getitem__(self, key):
        return self.sequences[key]

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

        self.gravity = 5
        self.velocity = Vector(*velocity)
        self.velocity_max = Vector(*maximum_velocity)
        self.acceleration = Vector(*initial_acceleration)


class ControllerComponent (Component):

    def __init__(self, owner):
        super(ControllerComponent, self).__init__(owner, "controllercomponent")
        self.move_left = False
        self.move_right = False
        self.jump = False


class MovementComponent(Component):

    def __init__(self, owner, position=(50, 50)):
        super(MovementComponent, self).__init__(owner, "movementcomponent")

        self.new_position = Vector(*position)
        self.old_position = Vector(*position)


class GeometryComponent(Component):

    def __init__(self, owner, position=(0, 0), dimensions=(10, 10), subsurf=None):
        super(GeometryComponent, self).__init__(owner, "geometrycomponent")

        # Scale each argument passed in, by the constant SCALE
        scaled_position = tuple(i * SCALE for i in position)
        scaled_dimensions = tuple(i * SCALE for i in dimensions)
        if subsurf:
            scaled_subsurface = tuple(i * SCALE for i in subsurf)
            self.src_rect = pygame.Rect(
                *(scaled_subsurface + scaled_dimensions))
        else:
            self.src_rect = pygame.Rect(0, 0, *scaled_dimensions)

        self.position = Vector(*scaled_position)
        self.dst_rect = pygame.Rect(*(scaled_position + scaled_dimensions))


class RenderComponent(Component):

    def __init__(self, owner, image=None, color=(255, 0, 255), make_reverse=False):
        super(RenderComponent, self).__init__(owner, "rendercomponent")

        self.trans_rect = pygame.Rect(0, 0, 0, 0)
        self.image_forward = None
        self.image = None
        self.image_reversed = None

        geo_cmp = owner.get_component("geometrycomponent")
        if not image:
            rect = geo_cmp.src_rect
            self.image = pygame.Surface((rect.w, rect.h)).convert_alpha()
            self.image.fill(color)
            return

        if type(image) == pygame.Surface:
            self.image_forward = image
        else:
            self.image_forward = load_image(IMAGE_DIR + image)

        self.image = self.image_forward

        if make_reverse == True:
            self.image_reversed = pygame.Surface(
                (self.image_forward.get_width(), self.image_forward.get_height()))
            self.image_reversed = self.image_reversed.convert_alpha()
            self.image_reversed.fill((0, 0, 0, 0))
            for x in range(0, self.image_forward.get_width(), geo_cmp.src_rect.width):
                self.image_reversed.blit(self.image_forward,
                                         pygame.Rect(self.image_forward.get_width(
                                         ) - x - geo_cmp.src_rect.width, 0, 0, 0),
                                         pygame.Rect(x, 0, geo_cmp.src_rect.width, geo_cmp.src_rect.height))

            self.image_reversed = pygame.transform.flip(
                self.image_reversed, True, False)

            self.image = self.image_reversed
