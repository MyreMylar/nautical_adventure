import pygame

from game.ui_text_button import UTTextButton


class PortUIWindow:
    def __init__(self, window_rect, fonts, port, player):
        self.window_rect = window_rect
        self.fonts = fonts
        self.background_colour = pygame.Color("#1A1A1A")
        self.text_colour = pygame.Color("#FFFFFF")
        self.port = port
        self.player = player

        self.window_title_str = self.port.name

        self.should_exit = False
        self.should_open_buy_goods_window = False
        self.should_open_sell_goods_window = False

        self.repair_cost = (self.player.max_health - self.player.health) * -2

        self.title_text_render = self.fonts[1].render(self.window_title_str, True, self.text_colour)
        self.export_text_render = self.fonts[0].render("Exports: " + self.port.export, True, self.text_colour)

        self.buy_button = UTTextButton([self.window_rect[0] + 40,
                                        self.window_rect[1] + 80, 70, 20],
                                       "Buy Goods", fonts, 0)
        self.sell_button = UTTextButton([self.window_rect[0] + 40,
                                         self.window_rect[1] + 110, 70, 20],
                                        "Sell Goods", fonts, 0)
        self.repair_button = UTTextButton([self.window_rect[0] + 40,
                                           self.window_rect[1] + 140, 70, 20],
                                          "Repair: " + str(self.repair_cost), fonts, 0)
        if abs(self.repair_cost) > self.player.gold:
            self.repair_button.disable()
        self.done_button = UTTextButton([self.window_rect[0] + 40, self.window_rect[1] + 180, 70, 20], "Done", fonts, 0)

    def handle_input_event(self, event):
        self.buy_button.handle_input_event(event)
        self.sell_button.handle_input_event(event)
        self.repair_button.handle_input_event(event)
        self.done_button.handle_input_event(event)

    def update(self):
        self.buy_button.update()
        self.sell_button.update()
        self.repair_button.update()
        self.done_button.update()

        if self.done_button.was_pressed():
            self.should_exit = True

        if self.buy_button.was_pressed():
            self.should_open_buy_goods_window = True

        if self.sell_button.was_pressed():
            self.should_open_sell_goods_window = True

        if self.repair_button.was_pressed():
            self.player.gold = self.player.gold + self.repair_cost
            self.player.health = self.player.max_health
            self.repair_cost = (self.player.max_health - self.player.health) * -2
            self.repair_button.set_text("Repair: " + str(self.repair_cost))

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

        self.buy_button.draw(screen)
        self.sell_button.draw(screen)
        self.repair_button.draw(screen)
        self.done_button.draw(screen)
