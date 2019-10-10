import pygame


class UITextEntryLine(pygame.sprite.Sprite):
    def __init__(self, position, width, font, ui_group):
        super().__init__(ui_group)
        self.selected = False
        self.position = position
        self.width = width
        self.font = font
        self.bg_colour = pygame.Color('#000000')
        self.text_colour = pygame.Color('#FFFFFF')
        self.text = ""

        self.horiz_line_padding = 4
        self.vert_line_padding = 3

        self.blink_cursor_time_acc = 0.0
        self.blink_cursor_time = 0.5
        self.cursor_on = False

        self.text_surface = self.font.render(self.text, True, self.text_colour)
        line_height = self.text_surface.get_rect().height

        self.cursor = pygame.Rect((self.text_surface.get_rect().right + 2,
                                   self.vert_line_padding), (1, line_height))

        self.image = pygame.Surface((self.width + (2 * self.horiz_line_padding),
                                     line_height + (2 * self.vert_line_padding)))
        self.rect = self.image.get_rect(x=position.x, y=position.y)
        self.redraw()

    def shutdown(self):
        self.kill()

    def redraw(self):
        self.image.fill(self.bg_colour)
        self.text_surface = self.font.render(self.text, True, self.text_colour)
        self.image.blit(self.text_surface, (self.horiz_line_padding, self.vert_line_padding))
        if self.cursor_on:
            self.cursor.x = self.text_surface.get_rect().right + self.horiz_line_padding
            pygame.draw.rect(self.image, self.text_colour, self.cursor)

        pygame.draw.rect(self.image, self.text_colour, self.image.get_rect(), 1)

    def update(self, time_delta, window_surface):
        if self.blink_cursor_time_acc >= self.blink_cursor_time:
            self.blink_cursor_time_acc = 0.0
            if self.cursor_on:
                self.cursor_on = False
                self.redraw()
            elif self.selected:
                self.cursor_on = True
                self.redraw()
        else:
            self.blink_cursor_time_acc += time_delta

    def deselect(self):
        self.selected = False
        self.redraw()

    def select(self):
        self.selected = True
        self.redraw()

    def process_event(self, event):
        processed_event = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                mouse_x, mouse_y = event.pos
                if self.rect.collidepoint(mouse_x, mouse_y):
                    self.select()

        if self.selected:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_BACKSPACE:
                    self.text = self.text[:-1]
                    self.redraw()
                else:
                    character = event.unicode
                    char_metrics = self.font.metrics(character)
                    if len(char_metrics) > 0 and char_metrics[0] is not None:
                        self.text += character
                        self.redraw()
