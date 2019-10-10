import math
import pygame
from pygame.locals import *

from game.tile import Tile
from game.map_editor_instructions_window import MapEditorInstructionsWindow


class MapEditor:
    def __init__(self, tiled_level, hud_rect, fonts):
        
        self.fonts = fonts
        self.editing_layer = 0
        self.tiled_level = tiled_level
        self.hud_rect = hud_rect
        
        self.left_mouse_held = False
        self.right_mouse_held = False

        self.need_to_refresh_tiles = True

        self.default_tile = [pygame.Rect(0, 0, 0, 0), self.tiled_level.tile_map[0][5], "grass_tile", True, None]
        self.held_tile_data = self.default_tile

        self.held_ai_spawn = None

        self.hovered_rec = None

        self.rotate_selected_tile_left = False
        self.rotate_selected_tile_right = False

        self.all_palette_tile_sprites = pygame.sprite.Group()
        self.all_ai_spawn_sprites = pygame.sprite.Group()

        self.palette_page = 0
        self.should_increase_palette_page = False
        self.should_decrease_palette_page = False

        self.palette_tiles = []
        self.palette_ai_spawns = []
        self.num_ai_spawns = 0
        self.tiles_per_page = 26
        all_tiles_and_ai = len(self.tiled_level.all_tile_data.keys()) + self.num_ai_spawns
        self.max_pages = int(math.ceil(all_tiles_and_ai / self.tiles_per_page))

        self.refresh_palette_tiles()

        self.left_scroll_held = False
        self.right_scroll_held = False
        self.up_scroll_held = False
        self.down_scroll_held = False

        self.map_position = self.tiled_level.find_player_start()

        self.map_editor_instructions = MapEditorInstructionsWindow([362, 100, 300, 250], fonts)

        self.rect_of_tile = None
            
    def refresh_palette_tiles(self):
        self.all_palette_tile_sprites.empty()
        self.palette_tiles[:] = []
        self.palette_ai_spawns[:] = []
        x_pos = 40
        y_pos = 40

        sorted_tile_keys = sorted(self.tiled_level.all_tile_data.keys())
        display_tile = self.palette_page * self.tiles_per_page

        max_tile = (self.palette_page * self.tiles_per_page) + self.tiles_per_page
        while display_tile < len(sorted_tile_keys) + self.num_ai_spawns and display_tile < max_tile:
            if display_tile < len(sorted_tile_keys):
                tile_data = sorted_tile_keys[display_tile]
                self.palette_tiles.append(Tile([self.hud_rect[0] + x_pos, self.hud_rect[1] + y_pos], 0,
                                               self.tiled_level.all_tile_data[tile_data], self.editing_layer))
                display_tile += 1

            x_pos += 72

            if x_pos > 904:
                x_pos = 40
                y_pos += 72

        for tile in self.palette_tiles:
            self.all_palette_tile_sprites.add(tile.sprite)

        for aiSpawn in self.palette_ai_spawns:
            self.all_palette_tile_sprites.add(aiSpawn.sprite)
            
    def run(self, screen, background, all_tile_sprites, all_top_tile_sprites, hud_rect, time_delta):
        running = True
        for event in pygame.event.get():
            if self.map_editor_instructions is not None:
                self.map_editor_instructions.handle_input_event(event)
            else:
                if event.type == QUIT:
                    self.tiled_level.save_tiles()
                    running = False
                if event.type == MOUSEBUTTONDOWN:
                    if event.button == 1:
                        self.left_mouse_held = True
                    if event.button == 3:
                        self.right_mouse_held = True
                if event.type == MOUSEBUTTONUP:
                    if event.button == 1:
                        self.left_mouse_held = False
                    if event.button == 3:
                        self.right_mouse_held = False
                if event.type == KEYDOWN:
                    if event.key == K_ESCAPE:
                        self.tiled_level.save_tiles()
                        running = False
                    if event.key == K_F5:
                        self.tiled_level.save_tiles()
                    if event.key == K_PERIOD:
                        self.rotate_selected_tile_right = True
                    if event.key == K_COMMA:
                        self.rotate_selected_tile_left = True
                    if event.key == K_UP:
                        self.up_scroll_held = True
                    if event.key == K_DOWN:
                        self.down_scroll_held = True
                    if event.key == K_LEFT:
                        self.left_scroll_held = True
                    if event.key == K_RIGHT:
                        self.right_scroll_held = True
                    if event.key == K_1:
                        self.editing_layer = 1
                    if event.key == K_0:
                        self.editing_layer = 0
                    if event.key == K_RIGHTBRACKET:
                        self.should_increase_palette_page = True
                    if event.key == K_LEFTBRACKET:
                        self.should_decrease_palette_page = True
                if event.type == KEYUP:
                    if event.key == K_UP:
                        self.up_scroll_held = False
                    if event.key == K_DOWN:
                        self.down_scroll_held = False
                    if event.key == K_LEFT:
                        self.left_scroll_held = False
                    if event.key == K_RIGHT:
                        self.right_scroll_held = False
            
        if self.map_editor_instructions is not None:
            self.map_editor_instructions.update()
            if self.map_editor_instructions.should_exit:
                self.map_editor_instructions = None

        if self.should_increase_palette_page:
            self.should_increase_palette_page = False
            if self.palette_page < self.max_pages - 1:
                self.palette_page += 1
            else:
                self.palette_page = 0  # loop back round
            self.refresh_palette_tiles()

        if self.should_decrease_palette_page:
            self.should_decrease_palette_page = False
            if self.palette_page > 0:
                self.palette_page -= 1
            else:
                self.palette_page = self.max_pages - 1  # loop back round
            self.refresh_palette_tiles()

        if self.up_scroll_held:
            self.map_position[1] -= 256.0 * time_delta
            if self.map_position[1] < self.tiled_level.initial_screen_offset[1]:
                self.map_position[1] = self.tiled_level.initial_screen_offset[1]
        if self.down_scroll_held:
            self.map_position[1] += 256.0 * time_delta
            if self.map_position[1] > \
                    (self.tiled_level.level_pixel_size[1] - self.tiled_level.initial_screen_offset[1]):
                self.map_position[1] = (self.tiled_level.level_pixel_size[1] -
                                        self.tiled_level.initial_screen_offset[1])
        if self.left_scroll_held:
            self.map_position[0] -= 256.0 * time_delta
            if self.map_position[0] < self.tiled_level.initial_screen_offset[0]:
                self.map_position[0] = self.tiled_level.initial_screen_offset[0]
        if self.right_scroll_held:
            self.map_position[0] += 256.0 * time_delta
            if self.map_position[0] > \
                    (self.tiled_level.level_pixel_size[0] - self.tiled_level.initial_screen_offset[0]):
                self.map_position[0] = (self.tiled_level.level_pixel_size[0] -
                                        self.tiled_level.initial_screen_offset[0])

        if self.rotate_selected_tile_right and self.held_tile_data[4] is not None:
            self.rotate_selected_tile_right = False
            self.held_tile_data[4].rotate_tile_right()
            self.need_to_refresh_tiles = True

        if self.rotate_selected_tile_left and self.held_tile_data[4] is not None:
            self.rotate_selected_tile_left = False
            self.held_tile_data[4].rotate_tile_left()
            self.need_to_refresh_tiles = True
        
        if self.left_mouse_held:
            click_pos = pygame.mouse.get_pos()
            if self.is_inside_hud(click_pos, hud_rect):
                self.held_tile_data = self.get_palette_tile_data_at_pos(click_pos)
                if self.held_tile_data is None:
                    self.held_ai_spawn = self.get_ai_spawn_data_at_pos(click_pos)
            else:
                self.held_tile_data = self.tiled_level.get_tile_data_at_pos(click_pos, self.editing_layer)

        if self.right_mouse_held:
            click_pos = pygame.mouse.get_pos()
            
            if self.is_inside_hud(click_pos, hud_rect):
                pass
            else:
                angle = 0
                if self.held_tile_data is not None:
                    if self.held_tile_data[4] is not None:
                        angle = self.held_tile_data[4].angle
                    self.rect_of_tile = self.tiled_level.set_tile_at_pos(click_pos,
                                                                         self.held_tile_data[2],
                                                                         angle, self.editing_layer)
                    self.need_to_refresh_tiles = True
                elif self.held_ai_spawn is not None:
                    self.tiled_level.addAISpawnAtPos(click_pos, self.held_ai_spawn)

        if self.tiled_level.update_offset_position(self.map_position, all_tile_sprites, all_top_tile_sprites):
            self.need_to_refresh_tiles = True

        self.all_ai_spawn_sprites.empty()
        for ai_spawn in self.tiled_level.ai_spawns:
            self.all_ai_spawn_sprites.add(ai_spawn.sprite)

        self.hovered_rec = self.tiled_level.get_tile_data_at_pos(pygame.mouse.get_pos(), self.editing_layer)[0]

        screen.blit(background, (0, 0))  # draw the background
        all_tile_sprites.draw(screen)
        self.all_ai_spawn_sprites.draw(screen)

        if self.editing_layer > 0:
            all_top_tile_sprites.draw(screen)

        if self.held_tile_data is not None:
            if not self.held_tile_data[3]:
                pygame.draw.rect(screen, pygame.Color(255, 100, 100),
                                 self.held_tile_data[0], 1)  # draw the selection rectangle
        if self.hovered_rec is not None:
            pygame.draw.rect(screen, pygame.Color(255, 225, 100), self.hovered_rec, 1)  # draw the selection rectangle

        layer_string = "Editing Layer: " + str(self.editing_layer)
        layer_string_render = self.fonts[0].render(layer_string, True, pygame.Color(255, 255, 255))
        screen.blit(layer_string_render, layer_string_render.get_rect(x=32, y=32))

        pygame.draw.rect(screen, pygame.Color(60, 60, 60), hud_rect, 0)  # draw the hud
        self.all_palette_tile_sprites.draw(screen)
        if self.held_tile_data is not None:
            if self.held_tile_data[3]:
                pygame.draw.rect(screen, pygame.Color(255, 100, 100),
                                 self.held_tile_data[0], 1)  # draw the selection rectangle

        if self.map_editor_instructions is not None:
            self.map_editor_instructions.draw(screen)

        pygame.display.flip()  # flip all our drawn stuff onto the screen

        return running

    @staticmethod
    def is_inside_hud(pos, hud_rect):
        if hud_rect[0] <= pos[0] and hud_rect[1] <= pos[1]:
            if hud_rect[0] + hud_rect[2] > pos[0] and hud_rect[1] + hud_rect[3] > pos[1]:
                return True
        return False

    def get_palette_tile_data_at_pos(self, click_pos):
        for tile in self.palette_tiles:
            if tile.sprite.rect[0] <= click_pos[0] and tile.sprite.rect[1] <= click_pos[1]:
                if tile.sprite.rect[0] + tile.sprite.rect[2] > click_pos[0] and\
                        tile.sprite.rect[1] + tile.sprite.rect[3] > click_pos[1]:
                    return [tile.sprite.rect, tile.tile_image, tile.tile_id, True, None]
        return None

    def get_ai_spawn_data_at_pos(self, click_pos):
        for aiSpawn in self.palette_ai_spawns:
            if aiSpawn.sprite.rect[0] <= click_pos[0] and aiSpawn.sprite.rect[1] <= click_pos[1]:
                if aiSpawn.sprite.rect[0] + aiSpawn.sprite.rect[2] > click_pos[0] and\
                        aiSpawn.sprite.rect[1] + aiSpawn.sprite.rect[3] > click_pos[1]:
                    return aiSpawn
        return None
