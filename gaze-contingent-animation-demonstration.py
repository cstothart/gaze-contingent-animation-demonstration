""" Gaze Contingent Animation Demo

Author: Cary Stothart
Date: 02/06/2017

This is a demonstration of gaze contingent animation using an Eyelink.

"""

import sys
import random
import time

import pygame
import pylink

class Shape:

    def __init__(self, x, y, size, px_per_second):
        self.color = (0, 0, 255)
        self.size = size
        self.pos = [x, y]
        self.old_pos_1 = []
        self.old_pos_2 = [x, y]
        self.d_x = random.choice([1, -1])
        self.d_y = random.choice([1, -1])
        self.px_per_second = px_per_second

    def update(self):
        self.old_pos_1.append([self.pos[0], self.pos[1]])
        if self.pos[0] < 0:
            self.pos[0] = 0
            self.d_x *= -1
            self.old_pos_1.append([self.pos[0], self.pos[1]])
        if self.pos[0] > task.width - self.size[0]:
            self.pos[0] = task.width - self.size[0]
            self.d_x *= -1
            self.old_pos_1.append([self.pos[0], self.pos[1]])
        if self.pos[1] < 0:
            self.pos[1] = 0
            self.d_y *= -1
            self.old_pos_1.append([self.pos[0], self.pos[1]])
        if self.pos[1] > task.height - self.size[1]:
            self.pos[1] = task.height - self.size[1]
            self.d_y *= -1
            self.old_pos_1.append([self.pos[0], self.pos[1]])
        for _obj in task.obj_list:
            if (task.objs_too_close(_obj.pos, _obj.size, self.pos, self.size)
                and _obj != self):
                if self.pos[0] < _obj.pos[0]:
                    self.d_x = -1
                    _obj.d_x = 1
                else:
                    self.d_x = 1
                    _obj.d_x = -1
                if self.pos[1] < _obj.pos[1]:
                    self.d_y = -1
                    _obj.d_y = 1
                else:
                    self.d_y = 1
                    _obj.d_y = -1
                _obj.old_pos_1.append([_obj.pos[0], _obj.pos[1]])
                _obj.pos[0] += ((_obj.px_per_second*_obj.d_x)*
                                  (task.ms_from_last_frame/1000.0))
                _obj.pos[1] += ((_obj.px_per_second*_obj.d_y)*
                                  (task.ms_from_last_frame/1000.0))
        self.pos[0] += ((self.px_per_second*self.d_x)*
                        (task.ms_from_last_frame/1000.0))
        self.pos[1] += ((self.px_per_second*self.d_y)*
                        (task.ms_from_last_frame/1000.0))
        self.old_pos_1.append([self.pos[0], self.pos[1]])
        if self.pos[0] == self.old_pos_2[0]:
            self.old_pos_1.append([self.pos[0], self.pos[1]])
            self.pos[0] += ((self.px_per_second*(self.d_x*(-1)))*
                            (task.ms_from_last_frame/1000.0))
            self.pos[1] += ((self.px_per_second*(self.d_y*(-1)))*
                            (task.ms_from_last_frame/1000.0))
        self.old_pos_2 = [self.pos[0], self.pos[1]]

    def draw(self):
        _x, _y = self.pos
        _width, _height = self.size
        _rect_list = []
        for _pos in self.old_pos_1:
            _rect_list.append(pygame.Rect(_pos[0], _pos[1], _width, _height))
        _big_dirty_rect = _rect_list[0].unionall(_rect_list)
        _big_dirty_rect.inflate_ip(task.obj_min_dist, task.obj_min_dist)
        task.dirty_rects.append(_big_dirty_rect)
        pygame.draw.rect(task.screen, self.color, (_x, _y, _width, _height))
        self.old_pos_1 = []


class VisualSearchTask:

    def __init__(self, display):
        pygame.init()
        self.max_fps = 60
        self.clock = pygame.time.Clock()
        self.px_per_second = 60
        self.bg_color = (255, 255, 255)
        self.obj_size = (70, 70)
        self.obj_min_dist = 0;
        self.dirty_rects = []
        self.obj_list = []
        self.screen = display
        self.screen.fill(self.bg_color)
        pygame.display.update()
        self.width = self.screen.get_size()[0]
        self.height = self.screen.get_size()[1]

    def get_gaze_pos(self):
        _dt = pylink.getEYELINK().getNewestSample()
        if(_dt != None):
            try:
                _pos = _dt.getRightEye().getGaze()
            except:
                _pos = _dt.getLeftEye().getGaze()
        else:
            _pos = ["NA", "NA"]
        return _pos

    def animation_loop(self):
        while 1:
            self.ms_from_last_frame = self.clock.tick(self.max_fps)
            pygame.display.update(self.dirty_rects)
            self.dirty_rects = []
            pygame.draw.rect(task.screen, task.bg_color,
                             (0, 0, self.width, self.height))
            for _obj in self.obj_list:
                _obj.update()
                _obj.draw()
            _dt = pylink.getEYELINK().getNewestSample()
            _gaze_position = self.get_gaze_pos()
            _gaze_rect = pygame.Rect(_gaze_position[0]-15,
                                     _gaze_position[1]-15, 30, 30)
            for _obj in self.obj_list:
                _obj_rect = pygame.Rect(_obj.pos[0], _obj.pos[1],
                                        _obj.size[0], _obj.size[1])
                if _gaze_rect.colliderect(_obj_rect):
                    _obj.color = (255, 0, 0)
                else:
                    _obj.color = (0, 0, 255)
            for event in pygame.event.get():
                if (event.type == pygame.KEYDOWN and
                    event.key == pygame.K_q):
                        pygame.quit()

    def objs_too_close(self, pos_1, size_1, pos_2, size_2):
        _rect_1 = pygame.Rect(pos_1[0], pos_1[1], size_1[0], size_1[1])
        _rect_2 = pygame.Rect(pos_2[0], pos_2[1], size_2[0], size_2[1])
        _rect_1.inflate_ip(self.obj_min_dist, self.obj_min_dist)
        _rect_2.inflate_ip(self.obj_min_dist, self.obj_min_dist)
        if _rect_1.colliderect(_rect_2):
            return True
        else:
            return False

    def create_and_place_objs(self, n_obj):
        _obj_pos_list = [(self.width/2-self.obj_size[0]/2,
                          self.height/2-self.obj_size[1]/2)]
        _n_obj = n_obj
        for _obj in range(1, _n_obj + 1):
            _flag = True
            while _flag:
                _flag = False
                _x = random.randrange(self.obj_size[0],
                                      self.width+1-self.obj_size[0]*2)
                _y = random.randrange(self.obj_size[1],
                                      self.height+1-self.obj_size[1]*2)
                _pos = (_x, _y)
                for _other_pos in _obj_pos_list:
                    if self.objs_too_close(_pos, self.obj_size,
                                           _other_pos, self.obj_size):
                        _flag = True
            _obj_pos_list.append((_x, _y))
            self.obj_list.append(Shape(_x, _y, self.obj_size,
                                       self.px_per_second))


class Display:
    def __init__(self, width, height):
        self.width = width
        self.height = height

    def setup_display(self):
        pygame.display.init()
        self.screen = pygame.display.set_mode((self.width, self.height),
                                               pygame.FULLSCREEN)
        pygame.mouse.set_visible(False)


class EyeTracker:
    def __init__(self, display):
        self.screen = display

    def setup_tracker(self, edf_file):
        self.edf_file = edf_file
        self.EYELINK = pylink.EyeLink()
        pylink.openGraphics()
        self.EYELINK.openDataFile(self.edf_file)
        pylink.flushGetkeyQueue()
        pylink.getEYELINK().setOfflineMode()
        self.surface = pygame.display.get_surface()
        pylink.getEYELINK().sendCommand("screen_pixel_coords =  0 0 %d %d"
                                        %(self.surface.get_rect().w - 1,
                                        self.surface.get_rect().h - 1))
        pylink.getEYELINK().sendMessage("DISPLAY_COORDS  0 0 %d %d"
                                        %(self.surface.get_rect().w - 1,
                                        self.surface.get_rect().h - 1))
        if self.EYELINK.getTrackerVersion() == 2:
            pylink.getEYELINK().sendCommand("select_parser_configuration 0")
        else:
            pylink.getEYELINK().sendCommand("saccade_velocity_threshold = 35")
            pylink.getEYELINK().sendCommand("saccade_acceleration_threshold=\
                                             9500")
        self.EYELINK.setFileEventFilter("LEFT,RIGHT,FIXATION,SACCADE,BLINK,\
                                         MESSAGE,BUTTON")
        self.EYELINK.setFileSampleFilter("LEFT,RIGHT,GAZE,AREA,GAZERES,\
                                          STATUS")
        self.EYELINK.setLinkEventFilter("LEFT,RIGHT,FIXATION,SACCADE,BLINK,\
                                          BUTTON")
        self.EYELINK.setLinkSampleFilter("LEFT,RIGHT,GAZE,GAZERES,AREA,\
                                          STATUS")
        pylink.getEYELINK().sendCommand("button_function 5\
                                         'accept_target_fixation'")
        pylink.setCalibrationColors((0, 0, 0), (251, 251, 251))
        pylink.setTargetSize(int(self.surface.get_rect().w/70),
                             int(self.surface.get_rect().w/300))
        pylink.setCalibrationSounds("", "", "")
        pylink.setDriftCorrectSounds("", "off", "off")

    def quit(self):
        pylink.getEYELINK().setOfflineMode()
        pylink.msecDelay(500)
        self.EYELINK.closeDataFile()
        self.EYELINK.receiveDataFile(self.edf_file, self.edf_file)
        self.EYELINK.close()
        pylink.closeGraphics()


if __name__ == "__main__":
    display = Display(0, 0)
    display.setup_display()
    et = EyeTracker(display.screen)
    et.setup_tracker("test.edf")
    pylink.getEYELINK().doTrackerSetup()
    et.EYELINK.startRecording(1, 1, 1, 1)
    pylink.beginRealTimeMode(100)
    task = VisualSearchTask(display.screen)
    task.create_and_place_objs(10)
    task.animation_loop()
    pylink.endRealTimeMode()
    pylink.getEYELINK().stopRecording()
    et.quit()

