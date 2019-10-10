import pygame
from pygame.locals import *


class UISlider:
    def __init__(self, rect, value_range, initial_value, fonts, font_size):
        self.fonts = fonts
        self.value_range = value_range
        self.initial_value = initial_value
        self.current_value = self.initial_value
        self.rect = rect
        self.should_slide_button = False
        self.is_hovered = True
        self.font_size = font_size
        self.slider_percentage = self.current_value / max(1, (self.value_range[1] - self.value_range[0]))

        self.button_colour = pygame.Color(75, 75, 75)
        self.back_ground_colour = pygame.Color(50, 50, 50)
        self.text_colour = pygame.Color("#FFFFFF")

        start_rect_position = (self.rect[2] - 50) * self.slider_percentage
        self.slider_button_rect = [self.rect[0] + start_rect_position, self.rect[1], 20, self.rect[3]]

        self.button_text_render = self.fonts[self.font_size].render(str(self.current_value), True, self.text_colour)

    def handle_input_event(self, event):
        if self.is_inside(pygame.mouse.get_pos()):
            if event.type == MOUSEBUTTONDOWN:
                if event.button == 1:
                    self.should_slide_button = True
                    
            if event.type == MOUSEBUTTONUP:
                if event.button == 1:
                    self.should_slide_button = False

    def get_value(self):
        return self.current_value

    def update(self):
        mouse_pos = pygame.mouse.get_pos()
        if self.is_inside(mouse_pos):
            if self.inside_button(mouse_pos):
                self.is_hovered = True
                self.button_colour = pygame.Color(100, 100, 100)
            else:
                self.is_hovered = False
                self.button_colour = pygame.Color(75, 75, 75)
        else:
            self.should_slide_button = False
            self.is_hovered = False
            self.button_colour = pygame.Color(75, 75, 75)

        if self.should_slide_button:
            self.slider_percentage = (mouse_pos[0] - (self.rect[0] + 10.0)) / (self.rect[2] - 50)
            if self.slider_percentage > 1.0:
                self.slider_percentage = 1.0
            if self.slider_percentage < 0.0:
                self.slider_percentage = 0.0
            if ((self.rect[0] + self.rect[2]) - 40) >= mouse_pos[0] >= self.rect[0] + 10:
                self.slider_button_rect = [mouse_pos[0] - 10, self.rect[1], 20, self.rect[3]]

            slider_width = ((self.value_range[1] - self.value_range[0]) * self.slider_percentage)
            self.current_value = int(self.value_range[0] + slider_width)
            self.button_text_render = self.fonts[self.font_size].render(str(self.current_value), True, self.text_colour)

    def set_max(self, new_max):
        self.value_range[1] = new_max
        self.current_value = 0
        self.slider_percentage = self.current_value / max(1, (self.value_range[1] - self.value_range[0]))
        start_rect_position = (self.rect[2] - 50) * self.slider_percentage
        self.slider_button_rect = [self.rect[0] + start_rect_position, self.rect[1], 20, self.rect[3]]
            
    def inside_button(self, screen_pos):
        is_inside = False
        if self.rect[0] <= screen_pos[0] <= self.rect[0]+self.rect[2]:
            if self.rect[1] <= screen_pos[1] <= self.rect[1]+self.rect[3]:
                is_inside = True
        return is_inside
    
    def is_inside(self, screen_pos):
        is_inside = False
        if self.slider_button_rect[0] <= screen_pos[0] <= self.slider_button_rect[0]+self.slider_button_rect[2]:
            if self.slider_button_rect[1] <= screen_pos[1] <= self.slider_button_rect[1]+self.slider_button_rect[3]:
                is_inside = True
        return is_inside

    def draw(self, screen):
        pygame.draw.rect(screen, self.back_ground_colour,
                         pygame.Rect(self.rect[0]+10, self.rect[1] + (self.rect[3]/2.0) - 2,
                                     self.rect[2]-50, 4), 0)
        pygame.draw.rect(screen, self.button_colour,
                         pygame.Rect(self.slider_button_rect[0], self.slider_button_rect[1],
                                     self.slider_button_rect[2], self.slider_button_rect[3]), 0)

        screen.blit(self.button_text_render,
                    self.button_text_render.get_rect(centerx=self.rect[0] + self.rect[2] - 20,
                                                     centery=self.rect[1] + self.rect[3]*0.5))
