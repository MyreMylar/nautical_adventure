import pygame
from ui.ui_text_button import UITextButton


class SliderBackground(pygame.sprite.Sprite):
    def __init__(self, rect, colour, ui_group):
        super().__init__(ui_group)
        self.rect = rect
        self.image = pygame.Surface((self.rect.width, self.rect.height))
        self.image.fill(colour)

    def process_event(self, event):
        pass


class UIHorizontalSlider:
    def __init__(self, top_left_position, dimensions, value_range, font, ui_group):
        self.font = font
        self.ui_group = ui_group

        self.left_limit_position = top_left_position.x + 20
        self.right_limit_position = top_left_position.x + dimensions[0] - 40

        self.background_colour = pygame.Color('#000000')
        self.background_rectangle = SliderBackground(pygame.Rect(top_left_position, dimensions), self.background_colour,
                                                     self.ui_group)

        self.left_button = UITextButton(top_left_position, (20, dimensions[1]), '<', self.font, self.ui_group)
        self.right_button = UITextButton(pygame.math.Vector2(top_left_position.x + dimensions[0] - 20,
                                                            top_left_position.y),
                                         (20, dimensions[1]), '>', self.font, self.ui_group)

        self.sliding_rect_position = pygame.math.Vector2(top_left_position.x + dimensions[0]/2 - 10,
                                                    top_left_position.y)
        self.sliding_button = UITextButton(self.sliding_rect_position,
                                           (20, dimensions[1]), ' ', self.font, self.ui_group)

    def shutdown(self):
        self.background_rectangle.kill()
        self.left_button.kill()
        self.right_button.kill()
        self.sliding_button.kill()

    def update(self, time_delta):
        if self.left_button.held and self.sliding_rect_position.x > self.left_limit_position:
            self.sliding_rect_position.x -= 75.0 * time_delta
            self.sliding_button.rect.x = self.sliding_rect_position.x
        elif self.right_button.held and self.sliding_rect_position.x < self.right_limit_position:
            self.sliding_rect_position.x += 75.0 * time_delta
            self.sliding_button.rect.x = self.sliding_rect_position.x

        if self.sliding_button.held:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            mouse_x -= 10  # offset mouse pos by 10 to center sliding button
            if self.right_limit_position > mouse_x > self.left_limit_position:
                self.sliding_rect_position.x = mouse_x
                self.sliding_button.rect.x = self.sliding_rect_position.x
