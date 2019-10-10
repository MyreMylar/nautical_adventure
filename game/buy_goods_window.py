import pygame

from game.ui_slider import UISlider
from game.ui_text_button import UTTextButton


class BuyGoodUILine:
    def __init__(self, good, position, fonts, player):
        self.fonts = fonts
        self.player = player
        self.position = position
        self.good = good[0]
        self.good_text = self.good.name
        self.good_value = good[1]
        affordable_max = int(self.player.gold / self.good_value)
        cargo_space_max = self.player.space_in_hold
        slider_max = min(affordable_max, cargo_space_max)
        self.test_slider = UISlider([self.position[0] + 80, self.position[1], 150, 20],
                                    [0, slider_max], 0, self.fonts, 0)
        self.buy_string = "Buy: " + str(self.good_value * self.test_slider.get_value() * -1)
        self.buy_button = UTTextButton([self.position[0] + 240, self.position[1], 80, 20],
                                       self.buy_string, self.fonts, 0)

        self.text_colour = pygame.Color(255, 255, 255)
        
        self.should_redraw_all_lines = False

        self.good_text_render = self.fonts[0].render(self.good_text, True, self.text_colour)

    def redraw(self):
        self.should_redraw_all_lines = False
        affordable_max = int(self.player.gold / self.good_value)
        cargo_space_max = self.player.space_in_hold
        slider_max = min(affordable_max, cargo_space_max)
        self.test_slider.set_max(slider_max)
        self.buy_string = "Buy: " + str(self.good_value * self.test_slider.get_value() * -1)
        self.buy_button.set_text(self.buy_string)

    def handle_input_event(self, event):
        self.test_slider.handle_input_event(event)
        self.buy_button.handle_input_event(event)

    def update(self):
        self.test_slider.update()
        self.buy_button.update()

        self.buy_string = "Buy: " + str(self.good_value * self.test_slider.get_value() * -1)
        self.buy_button.set_text(self.buy_string)
        if (self.good_value * self.test_slider.get_value()) > self.player.gold:
            self.buy_button.disable()

        if self.buy_button.was_pressed():
            self.player.gold = self.player.gold - (self.good_value * self.test_slider.get_value())
            self.should_redraw_all_lines = True
            self.player.add_goods([self.good, self.test_slider.get_value()])

    def draw(self, screen):
        self.test_slider.draw(screen)
        self.buy_button.draw(screen)

        screen.blit(self.good_text_render, self.good_text_render.get_rect(centerx=self.position[0],
                                                                          centery=self.position[1] + 10))
       

class BuyGoodsWindow:
    def __init__(self, window_rect, fonts, player, all_goods, port):

        self.port = port
        self.all_goods = all_goods
        self.window_rect = window_rect
        self.fonts = fonts
        self.back_ground_colour = pygame.Color(25, 25, 25)
        self.text_colour = pygame.Color(255, 255, 255)

        self.player = player
        
        self.should_exit = False

        self.window_title_str = "Buy Goods"
        self.button_text_render = self.fonts[1].render(self.window_title_str, True, self.text_colour)

        self.all_good_ui_lines = []
        counter = 0
        for good in self.port.buy_goods_and_prices:
            self.all_good_ui_lines.append(BuyGoodUILine(good,
                                                        [self.window_rect[0] + 40,
                                                         self.window_rect[1] + 50 + (counter * 25)],
                                                        fonts, player))
            counter += 1
        self.done_button = UTTextButton([self.window_rect[0] + self.window_rect[2] / 2 - 35,
                                         self.window_rect[1] + self.window_rect[3] - 30, 70, 20], "Done", fonts, 0)

    def handle_input_event(self, event):
        for ui_line in self.all_good_ui_lines:
            ui_line.handle_input_event(event)
        self.done_button.handle_input_event(event)

    def redraw_all_lines(self):
        for ui_line in self.all_good_ui_lines:
            ui_line.redraw()

    def update(self):
        for ui_line in self.all_good_ui_lines:
            ui_line.update()
        
        self.done_button.update()

        if self.done_button.was_pressed():
            self.should_exit = True
        redraw_all_lines = False
        for ui_line in self.all_good_ui_lines:
            if ui_line.should_redraw_all_lines:
                redraw_all_lines = True
        if redraw_all_lines:
            self.redraw_all_lines()

    def is_inside(self, screen_pos):
        is_inside = False
        if self.window_rect[0] <= screen_pos[0] <= self.window_rect[0] + self.window_rect[2]:
            if self.window_rect[1] <= screen_pos[1] <= self.window_rect[1] + self.window_rect[3]:
                is_inside = True
        return is_inside

    def draw(self, screen):
        pygame.draw.rect(screen, self.back_ground_colour,
                         pygame.Rect(self.window_rect[0], self.window_rect[1],
                                     self.window_rect[2], self.window_rect[3]), 0)

        screen.blit(self.button_text_render,
                    self.button_text_render.get_rect(centerx=self.window_rect[0] + self.window_rect[2] * 0.5,
                                                     centery=self.window_rect[1] + 24))

        for ui_line in self.all_good_ui_lines:
            ui_line.draw(screen)

        self.done_button.draw(screen)
