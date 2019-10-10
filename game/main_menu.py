import pygame
from pygame.locals import *

from game.ui_text_button import UTTextButton
from game.buy_goods_window import BuyGoodsWindow


class MainMenu:

    def __init__(self, fonts):
        self.show_menu = True
        self.show_editor = False

        self.is_start_game_selected = True
        self.is_run_editor_selected = False
        self.start_game = False

        self.background_image = pygame.image.load("images/menu_background.png")

        main_menu_title_string = "Nautical Adventure"
        self.main_menu_title_text_render = fonts[2].render(main_menu_title_string, True, pygame.Color(255, 255, 255))

        self.play_game_button = UTTextButton([437, 465, 150, 35], "Play Game", fonts, 1)
        self.edit_map_button = UTTextButton([437, 515, 150, 35], "Edit Map", fonts, 1)

        # self.buy_goods_window = BuyGoodsWindow([100, 100, 400, 350], fonts)

        self.running = True

    def run(self, screen, screen_data):
        is_main_menu_and_index = [0, 0]
        for event in pygame.event.get():
            self.play_game_button.handle_input_event(event)
            self.edit_map_button.handle_input_event(event)
            # self.buy_goods_window.handle_input_event(event)
            if event.type == QUIT:
                self.running = False

        self.play_game_button.update()
        self.edit_map_button.update()
        # self.buy_goods_window.update()

        if self.play_game_button.was_pressed():
            self.start_game = True
            self.show_menu = False

        if self.edit_map_button.was_pressed():
            self.show_editor = True
            self.show_menu = False
                    
        screen.blit(self.background_image, (0, 0))  # draw the background

        screen.blit(self.main_menu_title_text_render,  # draw the menu title
                    self.main_menu_title_text_render.get_rect(centerx=screen_data.screen_size[0] * 0.5,
                                                              centery=screen_data.screen_size[1] * 0.05))

        self.play_game_button.draw(screen)
        self.edit_map_button.draw(screen)
        # self.buy_goods_window.draw(screen)
                
        if self.show_editor:
            is_main_menu_and_index[0] = 2
        elif self.start_game:
            is_main_menu_and_index[0] = 1
        elif not self.running:
            is_main_menu_and_index[0] = 3
        else:
            is_main_menu_and_index[0] = 0

        return is_main_menu_and_index
