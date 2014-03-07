import pygame

class Timer(object):
    """ A class that updates fps and speedfactor
     requires: pygame"""

    def __init__(self):
        super(Timer, self).__init__()

        self.old_time = 0
        self.new_time = 0
        self.last_time = 0
        self.diff_time = 0
        self.speed_factor = 0
        self.num_frames = 0
        self.frames = 0


    def on_update(self):
        self.new_time = pygame.time.get_ticks()
        self.diff_time = self.new_time - self.last_time

        if self.new_time > self.old_time + 1000.:
            self.old_time = self.new_time
            self.frames = self.num_frames
            self.num_frames = 0

        self.speed_factor = self.diff_time / 1000. * 32.
        if self.speed_factor > 1:
            self.speed_factor = 1
        self.last_time = self.new_time
        self.num_frames += 1


class Animator(object):
    def __init__(self, rate):
        super(Animator, self).__init__()

        self.rate = rate

        self.new_time = 0
        self.last_time = 0
        self.diff_time = 0

        self.next_frame = 0
        self.current_frame = 0
        

    def on_update(self, sequence):
        self.new_time = pygame.time.get_ticks()

        if self.new_time > self.last_time + self.rate:
            self.last_time = self.new_time

            self.next_frame += 1

            if self.next_frame >= len(sequence):
                self.next_frame = 0;

            self.current_frame = sequence[self.next_frame]
