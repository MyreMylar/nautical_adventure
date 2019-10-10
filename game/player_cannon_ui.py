import pygame


class CannonUI:
    def __init__(self, start_pos, width, height, small_font):
        self.width = width
        self.height = height
        self.small_font = small_font
        self.position = [start_pos[0], start_pos[1]]

        self.base_rect = pygame.Rect(self.position[0], self.position[1], self.width, self.height)
        self.power_rect = pygame.Rect(self.position[0] + 1, self.position[1] + 1, 1, self.height - 2)
        self.reload_rect = pygame.Rect(self.position[0] + 1, self.position[1] + 1, self.width-2.0, self.height - 2)
        self.reload_percentage = 1.0

        self.cannon_label_text_render = self.small_font.render("Cannons:", True, pygame.Color(255, 255, 255))

    def update(self, reload_counter, reload_time):
        self.reload_percentage = reload_counter / reload_time
        if self.reload_percentage < 0.0:
            self.reload_percentage = 0.0
        reload_width = self.lerp(0.0, self.width - 2.0, self.reload_percentage)
        self.reload_rect = pygame.Rect(self.position[0] + 1, self.position[1] + 1, int(reload_width), self.height - 2)

    def draw(self, screen):

        text_rect = self.cannon_label_text_render.get_rect()
        screen.blit(self.cannon_label_text_render,
                    self.cannon_label_text_render.get_rect(centerx=self.position[0]-text_rect.width+12,
                                                           centery=self.position[1]+text_rect.height-3))
        pygame.draw.rect(screen, pygame.Color(0, 0, 0), self.base_rect, 0)
        pygame.draw.rect(screen, pygame.Color(100, 100, 100), self.reload_rect, 0)

        reloading_string = "Ready!"
        if self.reload_percentage < 1.0:
            reloading_string = "Reloading..."
            
        reloading_text_render = self.small_font.render(reloading_string, True, pygame.Color(255, 255, 255))
        screen.blit(reloading_text_render,
                    reloading_text_render.get_rect(x=self.position[0]+12,
                                                   centery=self.position[1]+text_rect.height-3))

    @staticmethod
    def lerp(a, b, c):
        return (c * b) + ((1.0 - c) * a)
