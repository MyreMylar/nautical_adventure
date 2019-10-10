import pygame
from text.text_funcs import FontDictionary, HTMLTextBlock
import pygame.gfxdraw


class UITooltip(pygame.sprite.Sprite):
    def __init__(self, html_text, bg_colour, shadow_image, font_dictionary, ui_sprite_group):
        super().__init__(ui_sprite_group)

        self.tool_tip_bg_colour = bg_colour
        width = 170
        horiz_padding = 8
        vert_padding = 8
        self.horiz_spacing = 4
        self.vert_spacing = 4
        text_block = HTMLTextBlock(html_text, (0, 0, width - (2*horiz_padding) - (2*self.horiz_spacing),
                                               -1), font_dictionary)
        self.text_surface = text_block.formatted_text_block.line_sprite

        height = self.text_surface.get_rect().height + (2*vert_padding) + (2*self.vert_spacing)

        self.rect = pygame.Rect((0, 0), (width, height))
        # should load this image elsewhere in a real program
        self.image = shadow_image
        self.image = pygame.transform.smoothscale(self.image, (width, height))
        pygame.draw.rect(self.image, self.tool_tip_bg_colour, pygame.Rect((self.horiz_spacing, self.vert_spacing),
                                                                          (width - (2*self.horiz_spacing),
                                                                           height-(2*self.vert_spacing))))
        pygame.draw.rect(self.image, pygame.Color("#000000"), pygame.Rect((self.horiz_spacing, self.vert_spacing),
                                                                          (width - (2 * self.horiz_spacing),
                                                                           height - (2 * self.vert_spacing))), 1)

        self.image.blit(self.text_surface, (self.horiz_spacing+horiz_padding, self.vert_spacing+vert_padding))

    def find_valid_position(self, position, camera_rect):
        # probably should just pass in a rectangle representing the dimensions of the window/screen not the surface
        # itself since we don't actually need that in here.
        self.rect.centerx = position.x
        self.rect.top = position.y + (2 * self.vert_spacing)

        window_rect = camera_rect.copy()

        if window_rect.contains(self.rect):
            return True
        else:
            if self.rect.bottom > window_rect.bottom:
                self.rect.bottom = position.y - (2 * self.vert_spacing)
            if self.rect.right > window_rect.right:
                self.rect.right = window_rect.right - self.horiz_spacing
            if self.rect.left < window_rect.left:
                self.rect.left = window_rect.left + self.horiz_spacing

        if window_rect.contains(self.rect):
            return True
        else:
            return False

    def process_event(self, event):
        pass
