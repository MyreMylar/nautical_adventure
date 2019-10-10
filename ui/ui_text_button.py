import pygame
from ui.ui_tool_tip import UITooltip


class UITextButton(pygame.sprite.Sprite):
    def __init__(self, position, dimensions, text, font, ui_group, tool_tip_text=None):
        super().__init__(ui_group)
        self.ui_group = ui_group
        self.font = font
        self.text = text

        # support for an optional 'tool tip' element attached to this button
        self.tool_tip_text = tool_tip_text
        self.tool_tip = None

        # colours, we could grab these from a separate colour theme class that we use across ui elements, much like a
        # css file provides colours and styles to a group of HTML we pages
        self.text_colour = pygame.Color('#000000')
        self.normal_colour = pygame.Color('#f9eaae')
        self.hover_colour = pygame.Color('#cdf9ae')

        # different states our button can be in, could use a state machine for this if you wanted
        # could also add a 'selected' state like windows has.
        self.hovered = False
        self.held = False
        self.pressed = False

        # time the hovering
        self.hover_time = 0.0
        self.tool_tip_appear_time = 1.0

        self.text_surface = self.font.render(self.text, True, self.text_colour)

        self.image = pygame.Surface(dimensions)
        self.rect = self.image.get_rect(x=position.x, y=position.y)

        # this helps us draw the text in the center of our button
        self.text_centred_rect = self.text_surface.get_rect(centerx=self.rect.centerx-self.rect.x,
                                                            centery=self.rect.centery-self.rect.y)

        self.redraw()

    def shutdown(self):
        self.kill()
        if self.tool_tip is not None:
            self.tool_tip.kill()

    def update(self, time_delta, window_surface):
        mouse_x, mouse_y = pygame.mouse.get_pos()

        if self.rect.collidepoint(mouse_x, mouse_y):
            if not self.hovered:
                self.hovered = True
                self.hover_time = 0.0
                self.redraw()

            if self.tool_tip is None and self.tool_tip_text is not None and self.hover_time > self.tool_tip_appear_time:
                self.tool_tip = UITooltip(self.tool_tip_text, self.ui_group)
                self.tool_tip.find_valid_position(pygame.math.Vector2(mouse_x, self.rect.centery), window_surface)

            self.hover_time += time_delta

        else:
            if self.hovered:
                self.hovered = False
                self.redraw()
                if self.tool_tip is not None:
                    self.tool_tip.kill()
                    self.tool_tip = None

            if self.held:
                self.held = False

    def process_event(self, event):
        processed_event = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                mouse_x, mouse_y = event.pos
                if self.rect.collidepoint(mouse_x, mouse_y):
                    self.held = True
                    processed_event = True
        if event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                mouse_x, mouse_y = event.pos
                if self.rect.collidepoint(mouse_x, mouse_y):
                    if self.held:
                        self.held = False
                        processed_event = True
                        self.pressed = True

        return processed_event

    def redraw(self):
        if self.hovered:
            self.image.fill(self.hover_colour)
        else:
            self.image.fill(self.normal_colour)

        self.image.blit(self.text_surface, self.text_centred_rect)

    def check_pressed_and_reset(self):
        if self.pressed:
            self.pressed = False
            return True
        else:
            return False
