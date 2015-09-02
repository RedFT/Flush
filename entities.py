import pygame

from components import *


class Entity(object):

    def __init__(self, collidable):
        super(Entity, self).__init__()

        self.collidable = True
        self.components = []
        self.systems = []

    def __getitem__(self, key):
        return self.get_component(key)

    def get_component(self, component_type):
        """ Iterate through component list for a component with
            the matching String """
        ret_cmp = next((comp for comp in self.components
                        if comp.component_type == component_type),
                       None)
        if ret_cmp == None:
            print self, "has no " + component_type
        return ret_cmp

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

        self.text = the_text


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
        self.components.append(GeometryComponent(self, (0, 0), (ww, wh)))

        self.target = None

        self.offset = Vector(offx, offy)
        self.velocity = Vector(vx, vy)

        self.elapsed = 0
        self.sinspeedx = .05
        self.sinspeedy = .10

    def follow(self, target):
        self.target = target


class Bullet(Entity):

    def __init__(self, position=(0, 0), direction=(1, 0)):
        super(Bullet, self).__init__(True)

        self.speed = 3

        self.components.append(PhysicsComponent(self,
                                                (direction[0] * self.speed,
                                                 direction[1] * self.speed),
                                                (10, 10),
                                                (0, 0)))
        self.components.append(GeometryComponent(self, (x, y), (2, 2)))
        self.components.append(RenderComponent(self))


class Tile(Entity):

    def __init__(self, image_filename, position=(0, 0), dimensions=(10, 10),
                 sub_surf=(0, 0)):
        super(Tile, self).__init__(True)

        self.components.append(GeometryComponent(self, position, dimensions,
                                                 sub_surf))
        self.components.append(RenderComponent(self, image_filename))


class SewerMan(Entity):

    def __init__(self, position=(0, 0)):
        super(SewerMan, self).__init__(True)

        self.face_left = False
        self.on_ground = False

        anim_cmp = AnimationComponent(self, 10)

        anim_cmp["walk"] = [1, 2, 1, 3, 4, 3, ]
        anim_cmp["stand"] = [0]
        anim_cmp["fall"] = [2]
        anim_cmp["slow"] = [1]
        anim_cmp.set_current_sequence("walk")

        self.components.append(anim_cmp)
        self.components.append(PhysicsComponent(
            self, (0, 0), (17, 20), (2, 2)))
        self.components.append(MovementComponent(self, position))
        self.components.append(GeometryComponent(self, position, (10, 10)))
        self.components.append(RenderComponent(
            self, 'SewerMan.png', make_reverse=True))
        self.components.append(ControllerComponent(self))

    def on_notify(self, entity, event):
        mov_cmp = self["movementcomponent"]
        phy_cmp = self["physicscomponent"]
        geo_cmp = self["geometrycomponent"]
        ctrl_cmp = self["controllercomponent"]

        if event == "up_pressed":
            ctrl_cmp.jump = True
        if event == "left_pressed":
            ctrl_cmp.move_left = True
        if event == "right_pressed":
            ctrl_cmp.move_right = True
        if event == "up_released":
            ctrl_cmp.jump = False
        if event == "left_released":
            ctrl_cmp.move_left = False
        if event == "right_released":
            ctrl_cmp.move_right = False

        if event == "collision":
            # Get rect before collision
            old_rect = pygame.Rect(
                mov_cmp.old_position.x, mov_cmp.old_position.y, geo_cmp.dst_rect.w, geo_cmp.dst_rect.h)

            # Get current rect of other entity
            other_rect = entity["geometrycomponent"].dst_rect

            # Get direction of colliding object
            direction = ""
            if old_rect.bottom <= other_rect.top:
                direction = "bottom"
            elif old_rect.top >= other_rect.bottom:
                direction = "top"
            elif old_rect.left >= other_rect.right:
                direction = "left"
            elif old_rect.right <= other_rect.left:
                direction = "right"

            # Respond to colliding object
            if direction == "right":
                phy_cmp.velocity.x *= -.5
                geo_cmp.position.x = other_rect.x - geo_cmp.dst_rect.w
            elif direction == "left":
                phy_cmp.velocity.x *= -.5
                geo_cmp.position.x = other_rect.right + 1
            elif direction == "top":
                geo_cmp.position.y = other_rect.bottom + 1
            elif direction == "bottom":
                self.on_ground = True
                geo_cmp.position.y = other_rect.top - geo_cmp.dst_rect.h
                # phy_cmp.velocity.y =

            geo_cmp.dst_rect.x, geo_cmp.dst_rect.y = geo_cmp.position
