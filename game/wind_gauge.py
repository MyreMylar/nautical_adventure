import pygame
import pygame.gfxdraw


class WindGauge:
    def __init__(self, start_pos, wind_min, wind_max, font):

        self.windMin = wind_min
        self.windMax = wind_max
        self.font = font
        
        self.radius = 48
        self.inner_radius = 16
        self.position = [int(start_pos[0]), int(start_pos[1])]
        self.wind_line_start_pos = [0.0, 0.0]
        self.wind_dir_point = [0.0, 0.0]
        
        self.wind_dir_arrow_corner1 = [0.0, 0.0]
        self.wind_dir_arrow_corner2 = [0.0, 0.0]

        self.wind_strength_text = "0"

        self.strength_text_render = self.font.render(self.wind_strength_text, True, pygame.Color(0, 0, 0))
        self.strength_text_render_rect = self.strength_text_render.get_rect(centerx=self.position[0],
                                                                            centery=self.position[1])

        self.north_text_render = self.font.render("N", True, pygame.Color(0, 0, 0))
        self.north_text_render_rect = self.north_text_render.get_rect(centerx=self.position[0],
                                                                      centery=self.position[1] - 62)

        self.south_text_render = font.render("S", True, pygame.Color(0, 0, 0))
        self.south_text_render_rect = self.south_text_render.get_rect(centerx=self.position[0],
                                                                      centery=self.position[1] + 65)

        self.east_text_render = font.render("E", True, pygame.Color(0, 0, 0))
        self.east_text_render_rect = self.east_text_render.get_rect(centerx=self.position[0] + 62,
                                                                    centery=self.position[1])

        self.west_text_render = font.render("W", True, pygame.Color(0, 0, 0))
        self.west_text_render_rect = self.west_text_render.get_rect(centerx=self.position[0] - 66,
                                                                    centery=self.position[1])

    def update_wind_direction_and_strength(self, wind):
        self.wind_strength_text = str(wind.current_value)
        self.wind_line_start_pos = [int(self.position[0] + (wind.direction[0] * self.inner_radius)),
                                    int(self.position[1] + (wind.direction[1] * self.inner_radius))]
        self.wind_dir_point = [int(self.position[0] + (wind.direction[0] * self.radius - 2)),
                               int(self.position[1] + (wind.direction[1] * self.radius - 2))]

        cross_wind = [wind.direction[1], -wind.direction[0]]
        
        self.wind_dir_arrow_corner1 = [(self.wind_dir_point[0]) - (wind.direction[0] * 10.0) + (cross_wind[0] * 8.0),
                                       (self.wind_dir_point[1]) - (wind.direction[1] * 10.0) + (cross_wind[1] * 8.0)]
        self.wind_dir_arrow_corner2 = [(self.wind_dir_point[0]) - (wind.direction[0] * 10.0) - (cross_wind[0] * 8.0),
                                       (self.wind_dir_point[1]) - (wind.direction[1] * 10.0) - (cross_wind[1] * 8.0)]

    def draw(self, screen):
        pygame.gfxdraw.aacircle(screen, self.position[0], self.position[1],
                                self.radius + 4, pygame.Color(0, 0, 0))
        pygame.gfxdraw.filled_circle(screen, self.position[0], self.position[1],
                              self.radius + 4, pygame.Color(0, 0, 0))
        pygame.gfxdraw.aacircle(screen, self.position[0], self.position[1],
                                self.radius, pygame.Color(200, 200, 200))
        pygame.gfxdraw.filled_circle(screen, self.position[0], self.position[1],
                              self.radius, pygame.Color(200, 200, 200))

        pygame.gfxdraw.aacircle(screen, self.position[0], self.position[1],
                                self.inner_radius, pygame.Color(230, 230, 230))
        pygame.gfxdraw.filled_circle(screen, self.position[0], self.position[1],
                              self.inner_radius, pygame.Color(230, 230, 230))

        pygame.draw.line(screen, pygame.Color(0, 0, 0), self.wind_line_start_pos, self.wind_dir_point, 2)
        pygame.draw.line(screen, pygame.Color(0, 0, 0), self.wind_dir_point, self.wind_dir_arrow_corner1, 2)
        pygame.draw.line(screen, pygame.Color(0, 0, 0), self.wind_dir_point, self.wind_dir_arrow_corner2, 2)

        screen.blit(self.strength_text_render, self.strength_text_render_rect)
        screen.blit(self.north_text_render, self.north_text_render_rect)
        screen.blit(self.south_text_render, self.south_text_render_rect)
        screen.blit(self.east_text_render, self.east_text_render_rect)
        screen.blit(self.west_text_render, self.west_text_render_rect)

    @staticmethod
    def lerp(a, b, c):
        return (c * b) + ((1.0 - c) * a)
