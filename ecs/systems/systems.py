import os
import pygame
from scipy.spatial import cKDTree as cKDTree
from math import sin

from pygame.font import Font

from constants import WIN_WIDTH, WIN_HEIGHT, FONT_DIR, SCALE
from ecs.ecs import System
from ecs.entities.entities import StaticText, Text, DynamicText, SewerMan, Tile
from retrogamelib.geometry import Vector
from utils import get_colorkey_hitmask, check_collision


class CameraSystem(System):
    def __init__(self, cam=None):
        super(CameraSystem, self).__init__()
        self.cam = cam

    def register_camera(self, cam):
        self.cam = cam

    def on_update(self, speed_factor):
        tgt_geo = self.cam.target["geometrycomponent"]
        cam_geo = self.cam["geometrycomponent"]

        distance = Vector((tgt_geo.position.x - cam_geo.position.x) + (tgt_geo.dst_rect.w / 2),
                          (tgt_geo.position.y - cam_geo.position.y) + (tgt_geo.dst_rect.h / 2))

        velocity = Vector(distance.x / self.cam.velocity.x,
                          distance.y / self.cam.velocity.y)

        cam_geo.position += velocity * speed_factor

        self.cam.elapsed += 1 * speed_factor

        x = (1 * (sin(self.cam.elapsed * self.cam.sinspeedx) * 4) + cam_geo.position.x)
        y = (1 * (sin(self.cam.elapsed * self.cam.sinspeedy) * 4) + cam_geo.position.y)

        cam_geo.dst_rect.x = x - self.cam.offset.x
        cam_geo.dst_rect.y = y - self.cam.offset.y

        self.translate_group(self.registered_entities)

    def translate_group(self, group):
        for other in group:
            other_ren = other["rendercomponent"]
            other_geo = other["geometrycomponent"]
            cam_geo = self.cam["geometrycomponent"]
            other_ren.trans_rect = pygame.Rect(other_geo.dst_rect.x, other_geo.dst_rect.y, 0, 0)
            other_ren.trans_rect.x -= cam_geo.dst_rect.x
            other_ren.trans_rect.y -= cam_geo.dst_rect.y

    def translate_rect(self, rect=[0, 0, 0, 0]):
        if not isinstance(rect, pygame.Rect):
            new_rect = pygame.Rect(rect[0], rect[1], rect[2], rect[3])
        else:
            new_rect = rect
        cam_geo = self.cam["geometrycomponent"]
        new_rect.x -= cam_geo.dst_rect.x
        new_rect.y -= cam_geo.dst_rect.y
        return new_rect

    def center_at(self, pos):
        self.cam.offset = pos
        self.cam.target = None


class TextSystem(System):
    def __init__(self, font_filename):
        super(TextSystem, self).__init__()

        self.font = Font(FONT_DIR + font_filename, 14)

    def on_update(self, speed_factor):
        for entity in self.registered_entities:
            if type(entity) == StaticText and not entity.loaded:
                render_cmp = entity["rendercomponent"]
                geo_cmp = entity["geometrycomponent"]

                entity.loaded = True
                render_cmp.image = self.font.render(entity.text,
                                                    False, entity.color)

                geo_cmp.src_rect.w = render_cmp.image.get_width()
                geo_cmp.src_rect.h = render_cmp.image.get_height()

            elif type(entity) == DynamicText:
                render_cmp = entity["rendercomponent"]
                geo_cmp = entity["geometrycomponent"]

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
            render_cmp = entity["rendercomponent"]
            geo_cmp = entity["geometrycomponent"]

            render_cmp.image = self.font.render("FPS: " + str(self.fps.frames) + " /s",
                                                False, (0, 0, 255))
            geo_cmp.src_rect.w = render_cmp.image.get_width()
            geo_cmp.src_rect.h = render_cmp.image.get_height()


class ControllerSystem(System):
    def __init__(self):
        super(ControllerSystem, self).__init__()

    def on_update(self, speed_factor):
        pass


class PlayerAnimationSystem(System):
    def __init__(self):
        super(PlayerAnimationSystem, self).__init__()

    def on_update(self, speed_factor):
        for entity in self.registered_entities:
            animation_cmp = entity["animationcomponent"]
            geo_cmp = entity["geometrycomponent"]

            # we need a funtion/method to get the state of the object(s)
            # and be able to override it
            # something like State get_state(self, entity)
            self.set_image(entity)
            self.set_sequence(entity)
            self.on_animate(entity)
            self.set_subsurface(geo_cmp, animation_cmp.curr_frame)

    def set_image(self, entity):
        render_cmp = entity["rendercomponent"]
        if entity.face_left:
            render_cmp.image = render_cmp.image_reversed
        elif not entity.face_left:
            render_cmp.image = render_cmp.image_forward

    def set_subsurface(self, geo_cmp, curr_frame):
        geo_cmp.src_rect.x = geo_cmp.dst_rect.w * curr_frame

    def set_sequence(self, entity):
        ctrl_cmp = entity["controllercomponent"]
        mov_cmp = entity["movementcomponent"]
        anim_cmp = entity["animationcomponent"]

        if isinstance(entity, SewerMan):
            if entity.on_ground and \
                    (mov_cmp.new_position.x != mov_cmp.old_position.x) and \
                    (not ctrl_cmp.move_left and not ctrl_cmp.move_right):
                if anim_cmp.curr_sequence != anim_cmp.sequences["slow"]:
                    anim_cmp.next_frame = 5
                anim_cmp.curr_sequence = anim_cmp.sequences["slow"]
            elif entity.on_ground and (ctrl_cmp.move_left or ctrl_cmp.move_right):
                if anim_cmp.curr_sequence != anim_cmp.sequences["walk"]:
                    anim_cmp.next_frame = 1
                anim_cmp.curr_sequence = anim_cmp.sequences["walk"]
            elif entity.on_ground:
                anim_cmp.curr_sequence = anim_cmp.sequences["stand"]
            elif not entity.on_ground:
                if anim_cmp.curr_sequence != anim_cmp.sequences["fall"]:
                    anim_cmp.next_frame = 5
                anim_cmp.curr_sequence = anim_cmp.sequences["fall"]

    def on_animate(self, entity):
        animation_cmp = entity["animationcomponent"]
        animation_cmp.new_time = pygame.time.get_ticks()

        if animation_cmp.new_time > animation_cmp.last_time + animation_cmp.rate:
            animation_cmp.last_time = animation_cmp.new_time

            animation_cmp.next_frame += 1

            if animation_cmp.next_frame >= len(animation_cmp.curr_sequence):
                animation_cmp.next_frame = 0;

            animation_cmp.curr_frame = animation_cmp.curr_sequence[animation_cmp.next_frame]


class PlayerMovementSystem(System):
    def __init__(self):
        super(PlayerMovementSystem, self).__init__()

    def on_update(self, speed_factor):
        for entity in self.registered_entities:
            ctrl_cmp = entity["controllercomponent"]
            move_cmp = entity["movementcomponent"]
            geo_cmp = entity["geometrycomponent"]
            physics_cmp = entity["physicscomponent"]
            render_cmp = entity["rendercomponent"]

            # event handling
            if ctrl_cmp.move_left:
                entity.face_left = True
                physics_cmp.velocity.x += -physics_cmp.acceleration.x * speed_factor
            elif ctrl_cmp.move_right:
                entity.face_left = False
                physics_cmp.velocity.x += physics_cmp.acceleration.x * speed_factor
            else:
                if physics_cmp.velocity.x > 1:
                    physics_cmp.velocity.x += -physics_cmp.acceleration.x * speed_factor
                elif physics_cmp.velocity.x < -1:
                    physics_cmp.velocity.x =  physics_cmp.velocity.x + (physics_cmp.acceleration.x * speed_factor)
                else:
                    physics_cmp.velocity.x = 0

            if entity.on_ground and ctrl_cmp.jump:
                physics_cmp.velocity.y = -physics_cmp.velocity_max.y * 1.1
            ctrl_cmp.jump = False
            entity.on_ground = False

            physics_cmp.velocity.y += physics_cmp.gravity * speed_factor

            # check velocity against limits
            if physics_cmp.velocity.y > physics_cmp.velocity_max.y:
                physics_cmp.velocity.y = physics_cmp.velocity_max.y
            if physics_cmp.velocity.x > physics_cmp.velocity_max.x:
                physics_cmp.velocity.x = physics_cmp.velocity_max.x
            if physics_cmp.velocity.y < -physics_cmp.velocity_max.y:
                physics_cmp.velocity.y = -physics_cmp.velocity_max.y
            if physics_cmp.velocity.x < -physics_cmp.velocity_max.x:
                physics_cmp.velocity.x = -physics_cmp.velocity_max.x

            move_cmp.old_position = geo_cmp.position
            move_cmp.new_position = move_cmp.old_position + (physics_cmp.velocity * speed_factor)
            geo_cmp.position = move_cmp.new_position

            geo_cmp.dst_rect.x, geo_cmp.dst_rect.y = geo_cmp.position.x, geo_cmp.position.y
            render_cmp.trans_rect = pygame.Rect(geo_cmp.dst_rect)


class EventSystem(System):
    def __init__(self):
        super(EventSystem, self).__init__()

        """
        listening_entities is a dictionary that contains
        a key (the event) and a value (list of entities that are
        listening for the event)
        """
        self.listening_entities = {}

    def on_update(self, speed_factor):
        pass

    def register(self, obj, event=None):  # event should be a string
        if event is None:
            super(EventSystem, self).register(obj)
        elif type(event) == list:
            for e in event:
                try:
                    the_list = self.listening_entities[e]
                    the_list.append(obj)
                except KeyError:
                    self.listening_entities[e] = [obj]
        else:
            try:
                the_list = self.listening_entities[event]
                the_list.append(obj)
            except KeyError:
                self.listening_entities[event] = [obj]

    def notify(self, entity, event):
        for ent in self.registered_entities:
            ent.on_notify(entity, event)
        try:
            for ent in self.listening_entities[event]:
                ent.on_notify(entity, event)
        except KeyError:
            pass


class Throwaway(object):
    def __init__(self):
        self.rect = None
        self.hitmask = None

class CollisionDetectionSystem(System):
    def __init__(self):
        super(CollisionDetectionSystem, self).__init__()

    def on_update(self, speed_factor):
        kd_input = [(ent["geometrycomponent"].position[0], ent["geometrycomponent"].position[1]) \
                    for ent in self.registered_entities]
        tree = cKDTree(kd_input, leafsize=1000)
        for ent_ind1, ent_pos in enumerate(kd_input):
            result = tree.query(ent_pos, k=5, distance_upper_bound=50)
            for ent_ind2 in result[1]:
                if ent_ind2 >= len(kd_input):
                    continue

                if ent_ind1 == ent_ind2:  # if same instance skip
                    continue

                ent1 = self.registered_entities[ent_ind1]
                ent2 = self.registered_entities[ent_ind2]

                if isinstance(ent1, Tile) and isinstance(ent2, Tile):  # if two tiles skip
                    continue

                if not ent1["geometrycomponent"].dst_rect.colliderect(ent2["geometrycomponent"].dst_rect):
                    continue
                # perform pixel perfect collision detection here
                obj1 = Throwaway()
                obj1.rect = ent1["geometrycomponent"].dst_rect
                obj1.hitmask = get_colorkey_hitmask(ent1["rendercomponent"].image, obj1.rect, True);
                obj2 = Throwaway()
                obj2.rect = ent2["geometrycomponent"].dst_rect
                obj2.hitmask = get_colorkey_hitmask(ent2["rendercomponent"].image, obj2.rect, True);

                if check_collision(obj1, obj2):
                    ent1.on_notify(ent2, "collision")
                    ent2.on_notify(ent1, "collision")


class RenderSystem(System):
    def __init__(self):
        super(RenderSystem, self).__init__()
        self.surf_main = pygame.display.get_surface()
        self.cam = None

    def register_camera(self, camera):
        self.cam = camera

    def on_update(self, speed_factor):
        for entity in self.registered_entities:
            render_cmp = entity["rendercomponent"]
            geo_cmp = entity["geometrycomponent"]

            if self.cam:
                if isinstance(entity, Text):
                    self.surf_main.blit(render_cmp.image, geo_cmp.dst_rect, geo_cmp.src_rect)
                elif self.cam["geometrycomponent"].dst_rect.colliderect(geo_cmp.dst_rect):
                    self.surf_main.blit(render_cmp.image, render_cmp.trans_rect,
                                        geo_cmp.src_rect)
            else:
                if pygame.Rect((0, 0, WIN_WIDTH, WIN_HEIGHT)).colliderect(geo_cmp.dst_rect):
                    self.surf_main.blit(render_cmp.image, render_cmp.trans_rect,
                                        geo_cmp.src_rect)
