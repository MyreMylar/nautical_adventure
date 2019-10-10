import pygame
from ui.ui_text_button import UITextButton


class UIExpandedDropDownState:
    def __init__(self, drop_down_menu_ui, options_list, selected_option, base_position_rect, font, close_button_width,
                 top_ui_group):
        self.drop_down_menu_ui = drop_down_menu_ui
        self.should_transition = False
        self.options_list = options_list
        self.selected_option = selected_option
        self.base_position_rect = base_position_rect
        self.font = font
        self.top_ui_group = top_ui_group
        self.close_button_width = close_button_width

        self.selected_option_button = None
        self.close_button = None
        self.menu_buttons = []

        self.should_transition = False
        self.target_state = 'closed'

    def start(self):
        self.should_transition = False
        option_y_pos = self.base_position_rect.y
        self.selected_option_button = UITextButton(pygame.math.Vector2(self.base_position_rect.x,
                                                                       self.base_position_rect.y),
                                                   (self.base_position_rect.width - self.close_button_width,
                                                    self.base_position_rect.height),
                                                   self.selected_option, self.font, self.top_ui_group)

        close_button_x = self.base_position_rect.x + self.base_position_rect.width - self.close_button_width
        self.close_button = UITextButton(pygame.math.Vector2(close_button_x,
                                                             self.base_position_rect.y),
                                         (self.close_button_width, self.base_position_rect.height),
                                         '∆', self.font, self.top_ui_group)

        option_y_pos -= self.selected_option_button.rect.height
        for option in self.options_list:
            new_button = UITextButton(pygame.math.Vector2(self.base_position_rect.x, option_y_pos),
                                      (self.base_position_rect.width - self.close_button_width,
                                       self.base_position_rect.height),
                                      option, self.font,
                                      self.top_ui_group)
            option_y_pos -= new_button.rect.height
            self.menu_buttons.append(new_button)

    def finish(self):
        for button in self.menu_buttons:
            button.kill()

        self.menu_buttons.clear()

        self.selected_option_button.kill()
        self.close_button.kill()

    def update(self):
        if self.close_button.check_pressed_and_reset():
            self.should_transition = True

        for button in self.menu_buttons:
            if button.check_pressed_and_reset():
                self.drop_down_menu_ui.selected_option = button.text
                self.should_transition = True


class UIClosedDropDownState:
    def __init__(self, drop_down_menu_ui, selected_option, base_position_rect, font, open_button_width, base_ui_group):
        self.drop_down_menu_ui = drop_down_menu_ui
        self.selected_option_button = None
        self.open_button = None
        self.selected_option = selected_option
        self.base_position_rect = base_position_rect
        self.font = font
        self.base_ui_group = base_ui_group

        self.open_button_width = open_button_width

        self.should_transition = False
        self.target_state = 'expanded'

    def start(self):
        self.should_transition = False
        self.selected_option_button = UITextButton(pygame.math.Vector2(self.base_position_rect.x,
                                                                       self.base_position_rect.y),
                                                   (self.base_position_rect.width - self.open_button_width,
                                                    self.base_position_rect.height),
                                                   self.selected_option, self.font, self.base_ui_group)
        open_button_x = self.base_position_rect.x + self.base_position_rect.width - self.open_button_width
        self.open_button = UITextButton(pygame.math.Vector2(open_button_x,
                                                            self.base_position_rect.y),
                                        (self.open_button_width, self.base_position_rect.height),
                                        '∆', self.font, self.base_ui_group)

    def finish(self):
        self.selected_option_button.kill()
        self.open_button.kill()

    def update(self):
        if self.open_button.check_pressed_and_reset():
            self.should_transition = True


class UIDropDownMenu:
    def __init__(self, options_list, starting_option, base_position_rect, font, base_ui_group, top_ui_group):
        self.font = font
        self.options_list = options_list
        self.selected_option = starting_option
        self.base_position_rect = base_position_rect
        self.base_ui_group = base_ui_group
        self.top_ui_group = top_ui_group
        self.open_button_width = 20

        self.menu_states = {'closed': UIClosedDropDownState(self,
                                                            self.selected_option,
                                                            self.base_position_rect,
                                                            self.font, self.open_button_width,
                                                            self.base_ui_group),
                            'expanded': UIExpandedDropDownState(self,
                                                                self.options_list, self.selected_option,
                                                                self.base_position_rect,
                                                                self.font, self.open_button_width, self.top_ui_group)}
        self.current_state = self.menu_states['closed']
        self.current_state.start()

    def shutdown(self):
        self.current_state.finish()

    def update(self):
        if self.current_state.should_transition:
            self.current_state.finish()
            self.current_state = self.menu_states[self.current_state.target_state]
            self.current_state.selected_option = self.selected_option
            self.current_state.start()

        self.current_state.update()
