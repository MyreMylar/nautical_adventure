import pygame


class HoverVillageWindow:
    def __init__(self, window_rect, fonts, village):
        self.window_rect = window_rect
        self.fonts = fonts
        self.background_colour = pygame.Color(25, 25, 25)
        self.text_colour = pygame.Color(255, 255, 255)
  
        self.village = village
        self.window_title_str = self.village.name
        self.export = self.village.export

        self.title_text_render = self.fonts[1].render(self.window_title_str, True, self.text_colour)
        self.export_text_render = self.fonts[0].render("Exports: " + self.export, True, self.text_colour)

    def handle_input_event(self, event):
        pass

    def update(self):
        pass   

    def is_inside(self, screen_pos):
        is_inside = False
        if self.window_rect[0] <= screen_pos[0] <= self.window_rect[0] + self.window_rect[2]:
            if self.window_rect[1] <= screen_pos[1] <= self.window_rect[1] + self.window_rect[3]:
                is_inside = True
        return is_inside

    def draw(self, screen):
        pygame.draw.rect(screen, self.background_colour,
                         pygame.Rect(self.window_rect[0], self.window_rect[1],
                                     self.window_rect[2], self.window_rect[3]), 0)

        screen.blit(self.title_text_render,
                    self.title_text_render.get_rect(centerx=self.window_rect[0] + self.window_rect[2] * 0.5,
                                                    centery=self.window_rect[1] + 24))

        screen.blit(self.export_text_render,
                    self.export_text_render.get_rect(centerx=self.window_rect[0] + self.window_rect[2] * 0.5,
                                                     centery=self.window_rect[1] + 50))
