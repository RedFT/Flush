import pygame
import os

from pygame.font import Font

from constants import WIN_WIDTH, WIN_HEIGHT, FONT_DIR, SCALE
from entities import Entity, StaticText, Text, DynamicText, SewerMan, Tile

from retrogamelib.geometry import Vector

from math import sin


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


class CameraSystem(System):

    def __init__(self, cam=None):
        super(CameraSystem, self).__init__()
        self.cam = cam

    def registerCamera(self, cam):
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
            other_ren.trans_rect = pygame.Rect(
                other_geo.dst_rect.x, other_geo.dst_rect.y, 0, 0)
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
            if type(entity) == StaticText and entity.loaded == False:
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


class ControllerSystem (System):

    def __init__(self):
        super(ControllerSystem, self).__init__()

    def on_update(self, speed_factor):
        pass


class AnimationSystem(System):

    def __init__(self):
        super(AnimationSystem, self).__init__()

    def on_update(self, speed_factor):
        for entity in self.registered_entities:
            anim_cmp = entity["animationcomponent"]
            geo_cmp = entity["geometrycomponent"]

            # we need a funtion/method to get the state of the object(s)
            # and be able to override it
            # something like State get_state(self, entity)
            self.set_image(entity)
            self.set_sequence(entity)
            self.on_animate(entity)
            self.set_subsurface(geo_cmp, anim_cmp.curr_frame)

    def set_image(self, entity):
        render_cmp = entity["rendercomponent"]
        if entity.face_left == True:
            render_cmp.image = render_cmp.image_reversed
        elif entity.face_left == False:
            render_cmp.image = render_cmp.image_forward

    def set_subsurface(self, geo_cmp, curr_frame):
        geo_cmp.src_rect.x = geo_cmp.dst_rect.w * curr_frame

    def set_sequence(self, entity):
        ctrl_cmp = entity["controllercomponent"]
        mov_cmp = entity["movementcomponent"]
        anim_cmp = entity["animationcomponent"]

        if isinstance(entity, SewerMan):
            if entity.on_ground == True and \
                    (mov_cmp.new_position.x != mov_cmp.old_position.x) and \
                    (not ctrl_cmp.move_left and not ctrl_cmp.move_right):
                if anim_cmp.curr_sequence != anim_cmp.sequences["slow"]:
                    anim_cmp.next_frame = 5
                anim_cmp.curr_sequence = anim_cmp.sequences["slow"]
            elif entity.on_ground == True and (ctrl_cmp.move_left or ctrl_cmp.move_right):
                if anim_cmp.curr_sequence != anim_cmp.sequences["walk"]:
                    anim_cmp.next_frame = 1
                anim_cmp.curr_sequence = anim_cmp.sequences["walk"]
            elif entity.on_ground == True:
                anim_cmp.curr_sequence = anim_cmp.sequences["stand"]
            elif entity.on_ground == False:
                if anim_cmp.curr_sequence != anim_cmp.sequences["fall"]:
                    anim_cmp.next_frame = 5
                anim_cmp.curr_sequence = anim_cmp.sequences["fall"]

    def on_animate(self, entity):
        anim_cmp = entity["animationcomponent"]
        anim_cmp.new_time = pygame.time.get_ticks()

        if anim_cmp.new_time > anim_cmp.last_time + anim_cmp.rate:
            anim_cmp.last_time = anim_cmp.new_time

            anim_cmp.next_frame += 1

            if anim_cmp.next_frame >= len(anim_cmp.curr_sequence):
                anim_cmp.next_frame = 0

            anim_cmp.curr_frame = anim_cmp.curr_sequence[anim_cmp.next_frame]


class MovementSystem(System):

    def __init__(self):
        super(MovementSystem, self).__init__()

    def on_update(self, speed_factor):
        for entity in self.registered_entities:
            ctrl_cmp = entity["controllercomponent"]
            move_cmp = entity["movementcomponent"]
            geo_cmp = entity["geometrycomponent"]
            physics_cmp = entity["physicscomponent"]
            render_cmp = entity["rendercomponent"]

            # event handling
            if ctrl_cmp.move_left == True:
                entity.face_left = True
                physics_cmp.velocity.x += -physics_cmp.acceleration.x * speed_factor
            elif ctrl_cmp.move_right == True:
                entity.face_left = False
                physics_cmp.velocity.x += physics_cmp.acceleration.x * speed_factor
            else:
                if physics_cmp.velocity.x > 1:
                    physics_cmp.velocity.x += -physics_cmp.acceleration.x * speed_factor
                elif physics_cmp.velocity.x < -1:
                    physics_cmp.velocity.x += physics_cmp.acceleration.x * speed_factor
                else:
                    physics_cmp.velocity.x = 0

            if entity.on_ground == True and ctrl_cmp.jump == True:
                physics_cmp.velocity.y = -physics_cmp.velocity_max.y
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
            move_cmp.new_position = move_cmp.old_position + \
                (physics_cmp.velocity * speed_factor)
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
        if event == None:
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
        for entity in self.registered_entities:
            entity.on_notify(entity, event)
        try:
            for entity in self.listening_entities[event]:
                entity.on_notify(entity, event)
        except KeyError:
            pass


class CollisionDetectionSystem(System):

    def __init__(self):
        super(CollisionDetectionSystem, self).__init__()
        length_or_width = 512
        self.minimum_search_area = pygame.Rect(
            0, 0, length_or_width, length_or_width)
        self.debug = False
        self.surf_main = pygame.display.get_surface()
        self.quads = []
        self.max_entities_per_quad = 40  # before returning from search_area

    def toggle_show_boxes(self):
        self.debug = not self.debug

    def search_area(self, depth, test_list, (low_x, high_x), (low_y, high_y)):
        """
        Quadtree search
        """

        entities_in_quadrant = []
        ret_list = []

        # quadrant itself
        quadrant_r = pygame.Rect(low_x, low_y, high_x - low_x, high_y - low_y)

        # dimensions of quadrant
        quadrant_size = pygame.Rect(0, 0, high_x - low_x, high_y - low_y)

        # check quadrant for entities
        entities_in_quadrant = [entity for entity in test_list if entity[
            "geometrycomponent"].dst_rect.colliderect(quadrant_r)]

        self.quads.append(quadrant_r)

        # break case 1: if quadrant is smaller than them minimum_search_area
        if (self.minimum_search_area.contains(quadrant_size)):
            return [entities_in_quadrant]

        # break case 2: if too many entities in a quadrant
        if (len(entities_in_quadrant) <= self.max_entities_per_quad):
            return [entities_in_quadrant]

        # split into quadrants
        div_line_x = (quadrant_r.w / 2) + quadrant_r.x
        div_line_y = (quadrant_r.h / 2) + quadrant_r.y

        ents_in_quad1 = self.search_area(depth, entities_in_quadrant,
                                         (low_x, div_line_x), (low_y, div_line_y))
        ents_in_quad2 = self.search_area(depth, entities_in_quadrant,
                                         (low_x, div_line_x), (div_line_y, high_y))
        ents_in_quad3 = self.search_area(depth, entities_in_quadrant,
                                         (div_line_x, high_x), (low_y, div_line_y))
        ents_in_quad4 = self.search_area(depth, entities_in_quadrant,
                                         (div_line_x, high_x), (div_line_y, high_y))

        for ents in [ents for ents in [ents_in_quad1, ents_in_quad2, ents_in_quad3, ents_in_quad4] if len(ents) > 0]:
            for lst in ents:
                if lst not in ret_list and any([ent for ent in lst if not isinstance(ent, Tile)]):
                    ret_list = ret_list + [lst]

        return ret_list

    def on_update(self, speed_factor):
        self.quads = []
        largest_x = max(
            [ent["geometrycomponent"].dst_rect.right for ent in self.registered_entities])
        largest_y = max(
            [ent["geometrycomponent"].dst_rect.bottom for ent in self.registered_entities])
        smallest_x = min(
            [ent["geometrycomponent"].position.x for ent in self.registered_entities])
        smallest_y = min(
            [ent["geometrycomponent"].position.y for ent in self.registered_entities])

        list_to_test = self.search_area(0, self.registered_entities,
                                        (smallest_x, largest_x), (smallest_y, largest_y))

        num_checks = 0
        num_collisions = 0
        new_list = []
        for lst in list_to_test:
            new_list += lst
        my_set = set(new_list)
        for ent1 in my_set:
            for ent2 in my_set:
                if ent1 == ent2:  # if same instance skip
                    continue

                if isinstance(ent1, Tile) and isinstance(ent2, Tile):  # if two tiles skip
                    continue
                num_checks += 1
                if ent1["geometrycomponent"].dst_rect.colliderect(
                        ent2["geometrycomponent"].dst_rect):
                    num_collisions += 1
                    ent1.on_notify(ent2, "collision")
                    ent2.on_notify(ent1, "collision")

        os.system("clear")
        print "-- Collision Stats --"
        print "{:<4} collision checks, \n{:<4} objects, \n{:<4} collision(s), \n{:<4} quads explored, \n{:<4} max entities per quadrant".format(num_checks, len(my_set), num_collisions, len(self.quads), self.max_entities_per_quad)

    def draw_quads(self, camera_sys):
        if self.debug == False:
            return
        for quad in self.quads:
            pygame.draw.rect(self.surf_main, (255, 255, 0),
                             camera_sys.translate_rect(quad), 1)


class RenderSystem(System):

    def __init__(self):
        super(RenderSystem, self).__init__()
        self.surf_main = pygame.display.get_surface()
        self.cam = None

    def registerCamera(self, camera):
        self.cam = camera

    def on_update(self, speed_factor):
        for entity in self.registered_entities:
            render_cmp = entity["rendercomponent"]
            geo_cmp = entity["geometrycomponent"]

            if self.cam:
                if isinstance(entity, Text):
                    self.surf_main.blit(
                        render_cmp.image, geo_cmp.dst_rect, geo_cmp.src_rect)
                elif self.cam["geometrycomponent"].dst_rect.colliderect(geo_cmp.dst_rect):
                    self.surf_main.blit(render_cmp.image, render_cmp.trans_rect,
                                        geo_cmp.src_rect)
            else:
                if pygame.Rect((0, 0, WIN_WIDTH, WIN_HEIGHT)).colliderect(geo_cmp.dst_rect):
                    self.surf_main.blit(render_cmp.image, render_cmp.trans_rect,
                                        geo_cmp.src_rect)
