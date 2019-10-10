import pygame

from game.ui_slider import UISlider
from game.ui_text_button import UTTextButton


class SellGoodUILine:
    def __init__(self, good_and_quantity, sell_goods_and_prices, position, fonts, player):
        self.fonts = fonts
        self.player = player
        self.position = position
        self.good_and_quantity = good_and_quantity
        self.good_text = good_and_quantity[0].name

        self.good_value = 0
        for good in sell_goods_and_prices:
            if good[0].name == good_and_quantity[0].name:
                self.good_value = good[1]
        self.test_slider = UISlider([self.position[0] + 80, self.position[1], 150, 20],
                                    [0, self.good_and_quantity[1]], 0, self.fonts, 0)
        self.sell_string = "Sell: +" + str(self.good_value * self.test_slider.get_value())
        self.sell_button = UTTextButton([self.position[0] + 240, self.position[1], 80, 20],
                                        self.sell_string, self.fonts, 0)

        self.text_colour = pygame.Color("#FFFFFF")
        
        self.should_redraw_all_lines = False

        self.good_text_render = self.fonts[0].render(self.good_text, True, self.text_colour)

    def redraw(self):
        self.should_redraw_all_lines = False
        self.test_slider.set_max(self.good_and_quantity[1])
        self.sell_string = "Sell: +" + str(self.good_value * self.test_slider.get_value())
        self.sell_button.set_text(self.sell_string)

    def handle_input_event(self, event):
        self.test_slider.handle_input_event(event)
        self.sell_button.handle_input_event(event)

    def update(self):
        self.test_slider.update()
        self.sell_button.update()

        self.sell_string = "Sell: +" + str(self.good_value * self.test_slider.get_value())
        self.sell_button.set_text(self.sell_string)
        
        if self.sell_button.was_pressed():
            self.player.gold = self.player.gold + (self.good_value * self.test_slider.get_value())
            self.should_redraw_all_lines = True
            self.player.remove_goods([self.good_and_quantity[0], self.test_slider.get_value()])

    def draw(self, screen):
        self.test_slider.draw(screen)
        self.sell_button.draw(screen)

        screen.blit(self.good_text_render, self.good_text_render.get_rect(centerx=self.position[0],
                                                                          centery=self.position[1] + 10))


class SellGoodsWindow:
    def __init__(self, window_rect, fonts, player, all_goods, port):

        self.port = port
        self.all_goods = all_goods
        self.window_rect = window_rect
        self.fonts = fonts
        self.background_colour = pygame.Color("#1A1A1A")
        self.text_colour = pygame.Color("#FFFFFF")

        self.player = player
        
        self.should_exit = False

        self.window_title_str = "Sell Goods"
        self.button_text_render = self.fonts[1].render(self.window_title_str, True, self.text_colour)

        self.all_good_ui_lines = []
        counter = 0
        for good in self.all_goods:
            self.all_good_ui_lines.append(SellGoodUILine(good,
                                                         self.port.sell_goods_and_prices,
                                                         [self.window_rect[0] + 40,
                                                          self.window_rect[1] + 50 + (counter * 25)],
                                                         fonts, player))
            counter += 1
        self.doneButton = UTTextButton([self.window_rect[0] + self.window_rect[2] / 2 - 35,
                                        self.window_rect[1] + self.window_rect[3] - 30, 70, 20], "Done", fonts, 0)

    def handle_input_event(self, event):
        for uiLine in self.all_good_ui_lines:
            uiLine.handle_input_event(event)
        self.doneButton.handle_input_event(event)

    def redraw_all_lines(self):
        for uiLine in self.all_good_ui_lines:
            uiLine.redraw()

    def update(self):
        for uiLine in self.all_good_ui_lines:
            uiLine.update()
        
        self.doneButton.update()

        if self.doneButton.was_pressed():
            self.should_exit = True
        redraw_all_lines = False
        for uiLine in self.all_good_ui_lines:
            if uiLine.should_redraw_all_lines:
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
        pygame.draw.rect(screen, self.background_colour, pygame.Rect(self.window_rect[0], self.window_rect[1],
                                                                     self.window_rect[2], self.window_rect[3]), 0)

        screen.blit(self.button_text_render,
                    self.button_text_render.get_rect(centerx=self.window_rect[0] + self.window_rect[2] * 0.5,
                                                     centery=self.window_rect[1] + 24))

        for uiLine in self.all_good_ui_lines:
            uiLine.draw(screen)

        self.doneButton.draw(screen)
