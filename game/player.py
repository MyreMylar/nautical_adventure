import math
import random
import pygame
from pygame.locals import *

from game.cannonball import Cannonball
from game.port_ui_window import PortUIWindow
from text.text_funcs import FontDictionary
from game.hover_village_window import HoverVillageWindow
from ui.ui_tool_tip import UITooltip
from game.buy_goods_window import BuyGoodsWindow
from game.sell_goods_window import SellGoodsWindow


class Player:
    def __init__(self, tiled_level, start_pos, explosion_sprite_sheet, hud_buttons, all_trade_goods):

        self.xp = 0
        self.level = 1
        self.score = 0
        self.all_trade_goods = all_trade_goods
        self.hold_size = 250
        self.space_in_hold = self.hold_size
        self.goods_in_hold = []
        self.gold = 100
        self.image_name = "images/sailing_ship.png"
        self.explosion_sprite_sheet = explosion_sprite_sheet
        self.original_image = pygame.image.load(self.image_name)

        self.font_dict = FontDictionary()
        self.font_dict.add_font_path("verdana",
                                font_path="fonts/verdana.ttf",
                                bold_path="fonts/verdanab.ttf",
                                italic_path="fonts/verdanai.ttf",
                                bold_italic_path="fonts/verdanaz.ttf")

        self.ui_shadow_image = pygame.image.load('images/ui_shadow.png').convert_alpha()

        self.hud_buttons = hud_buttons

        for button in self.hud_buttons:
            if button.button_image_name == "bow_icon":
                button.set_selected()
            else:
                button.clear_selected()

        self.sprite = pygame.sprite.Sprite()
        self.test_collision_sprite = pygame.sprite.Sprite()
        self.flash_sprite = pygame.sprite.Sprite()
        self.sprite.image = self.original_image
        self.sprite.rect = self.original_image.get_rect()

        self.collide_radius = 18

        self.sprite.rect.center = start_pos

        self.sprite_rot_offset = [0.0, 0.0]
        self.speed = 0.0
        self.acceleration = 0.0
        self.max_speed = 125.0

        self.max_health = 200
        self.health = self.max_health

        self.should_die = False

        self.move_accumulator = 0.0

        self.position = [float(self.sprite.rect.center[0]), float(self.sprite.rect.center[1])]
        self.playerMoveTarget = self.position

        self.current_vector = [0.0, -1.0]

        self.screen_position = [0, 0]
        self.screen_position[0] = self.position[0]
        self.screen_position[1] = self.position[1]

        self.update_screen_position(tiled_level.position_offset)

        self.new_facing_angle = math.atan2(-self.current_vector[0], -self.current_vector[1]) * 180 / math.pi

        self.target_vector = [0.0, -1.0]
        self.target_angle = self.new_facing_angle

        self.sprite.rect.center = self.rot_point([self.screen_position[0],
                                                  self.screen_position[1] + self.sprite_rot_offset[1]],
                                                 self.screen_position, -self.new_facing_angle)

        self.left_mouse_held = False
        self.right_mouse_held = False

        self.reload_counter = 3.0
        self.reload_time = 3.0
        self.can_fire = True

        self.per_cannonball_damage = 20

        self.player_fire_target = [10000, 10000]

        self.sprite_flash_acc = 0.0
        self.sprite_flash_time = 0.15
        self.should_flash_sprite = False

        self.is_collided = False

        self.firing = False
        self.firing_timer = 0.0

        self.has_new_high_score = False

        self.in_port = False

        self.port_ui_window = None
        self.port_we_are_in = None

        self.hovering_village = False
        self.hover_village_window = None

        self.hovered_village = None

        self.buy_goods_window = None
        self.buying_goods = False
        self.should_open_buy_goods_window = False

        self.sell_goods_window = None
        self.should_open_sell_goods_window = False

        self.water_resistance = -25.0

        self.collide_col = pygame.Color(180, 180, 180)

        self.circle1_centre = [self.screen_position[0] + (self.current_vector[0] * 16),
                               self.screen_position[1] + (self.current_vector[1] * 16)]
        self.circle2_centre = [self.screen_position[0] + (self.current_vector[0] * -16),
                               self.screen_position[1] + (self.current_vector[1] * -16)]
        self.circle3_centre = self.screen_position

        self.fire_vector = [0.0, 0.0]

    def add_random_cargo(self):
        number_of_types = random.randint(1, 5)
        for i in range(0, number_of_types):
            random_good = random.choice(self.all_trade_goods)
            random_amount = random.randint(1, 20)
            self.add_goods([random_good, random_amount])

    def add_goods(self, goods):
        found_good = False
        if self.space_in_hold > 0:
            if goods[1] > self.space_in_hold:
                goods[1] = self.space_in_hold
            for good in self.goods_in_hold:
                if good[0] == goods[0]:
                    found_good = True
                    good[1] += goods[1]
            if not found_good:
                self.goods_in_hold.append(goods)

        self.space_in_hold = self.hold_size - self.total_goods_in_hold()

    def remove_goods(self, goods):
        remove_index = -1
        list_index = 0
        for good in self.goods_in_hold:
            if good[0] == goods[0]:
                good[1] -= goods[1]
                if good[1] == 0:
                    remove_index = list_index
            list_index += 1

        if remove_index != -1:
            del self.goods_in_hold[remove_index]

        self.space_in_hold = self.hold_size - self.total_goods_in_hold()

    def total_goods_in_hold(self):
        total = 0
        for good in self.goods_in_hold:
            total += good[1]

        return total

    def add_xp(self, xp):
        self.xp += xp

    def add_score(self, score):
        self.score += score

    def xp_for_next_level(self):
        # 2 = 100
        # 3 = 250
        # 4 = 500
        # 5 = 850
        # 6 = 1300
        # 7 = 1850
        return 50 + (100 * ((self.level * self.level) / 2))

    @staticmethod
    def get_world_position_from_screen_pos(screen_pos, world_offset):
        world_pos = [0, 0]
        world_pos[0] = screen_pos[0] + world_offset[0]
        world_pos[1] = screen_pos[1] + world_offset[1]

        return world_pos

    def update_screen_position(self, world_offset):
        self.screen_position[0] = self.position[0] - world_offset[0]
        self.screen_position[1] = self.position[1] - world_offset[1]

    def update_sprite(self, all_sprites, time_delta):
        all_sprites.add(self.sprite)

        if self.should_flash_sprite:
            self.sprite_flash_acc += time_delta
            if self.sprite_flash_acc > self.sprite_flash_time:
                self.sprite_flash_acc = 0.0
                self.should_flash_sprite = False
            else:
                lerp_value = self.sprite_flash_acc / self.sprite_flash_time
                flash_alpha = self.lerp(255, 0, lerp_value)
                flash_image = self.sprite.image.copy()
                flash_image.fill((0, 0, 0, flash_alpha), None, pygame.BLEND_RGBA_MULT)
                flash_image.fill((255, 255, 255, 0), None, pygame.BLEND_RGBA_ADD)
                self.flash_sprite.image = flash_image
                self.flash_sprite.rect = self.flash_sprite.image.get_rect()
                self.flash_sprite.rect.center = self.rot_point([self.screen_position[0],
                                                                self.screen_position[1] + self.sprite_rot_offset[1]],
                                                               self.screen_position, -self.new_facing_angle)
                all_sprites.add(self.flash_sprite)
        return all_sprites

    def process_event(self, event):
        if self.port_ui_window is not None:
            self.left_mouse_held = False
            self.right_mouse_held = False
            self.port_ui_window.handle_input_event(event)
        elif self.buy_goods_window is not None:
            self.buy_goods_window.handle_input_event(event)
        elif self.sell_goods_window is not None:
            self.sell_goods_window.handle_input_event(event)
        else:
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
                pass

    def update_movement_and_collision(self, time_delta, projectiles, tiled_level,
                                      monsters, all_ui_windows, ui_sprite_group,
                                      fonts, wind):
        direction_magnitude = math.sqrt(
            self.current_vector[0] * self.current_vector[0] + self.current_vector[1] * self.current_vector[1])
        unit_dir_vector = [self.current_vector[0] / direction_magnitude, self.current_vector[1] / direction_magnitude]
        dot_wind = unit_dir_vector[0] * wind.direction[0] + unit_dir_vector[1] * wind.direction[1]

        if self.health == 0:
            self.should_die = True

        if not self.in_port and self.port_ui_window is None:
            hovering_any_village = False
            mouse_pos = pygame.mouse.get_pos()
            for village in tiled_level.villages:
                if (village.position[0] - 32) <= mouse_pos[0] <= (village.position[0] + 32):
                    if (village.position[1] - 32) <= mouse_pos[1] <= (village.position[1] + 32):
                        hovering_any_village = True
                        self.hovered_village = village
            if hovering_any_village and not self.hovering_village:
                self.hovering_village = True
                self.hover_village_window = UITooltip("<font size=5 face=verdana>{}</font>"
                                                      "<br>"
                                                      "<font size=2 face=verdana><b>Main Export: </b>"
                                                      "{}</font>".format(self.hovered_village.name,
                                                                         self.hovered_village.export),
                                                      pygame.Color("#191919"),
                                                      self.ui_shadow_image,
                                                      self.font_dict,
                                                      ui_sprite_group)
                self.hover_village_window.find_valid_position(pygame.math.Vector2(mouse_pos[0], mouse_pos[1]),
                                                              pygame.Rect((0, 0), (1024, 600)))
                #HoverVillageWindow([437, 150, 150, 75], fonts, self.hovered_village)
            if not hovering_any_village and self.hovering_village:
                self.hovering_village = False
                self.hovered_village = None
                if self.hover_village_window is not None:
                    self.hover_village_window.kill()
                    self.hover_village_window = None

        in_any_port = False
        for village in tiled_level.villages:
            if self.test_point_in_circle(self.position, village.world_position, village.port_radius):
                in_any_port = True
                self.port_we_are_in = village
        if in_any_port and not self.in_port and self.port_ui_window is None:
            self.speed = 0.0
            self.in_port = True
            self.port_ui_window = PortUIWindow([437, 100, 150, 240], fonts, self.port_we_are_in, self)
            all_ui_windows.append(self.port_ui_window)

            if self.hover_village_window is not None:
                self.hovering_village = False
                self.hovered_village = None
                self.hover_village_window.kill()
                self.hover_village_window = None
        if not in_any_port and self.in_port:
            # possible to drift out of port while still in menus atm
            if self.port_ui_window is None and self.buy_goods_window is None and self.sell_goods_window is None:
                self.in_port = False
                self.port_we_are_in = None

        if self.port_ui_window is not None:
            if self.port_ui_window.should_open_buy_goods_window:
                all_ui_windows.remove(self.port_ui_window)
                self.port_ui_window = None
                self.should_open_buy_goods_window = True

        if self.port_ui_window is not None:
            if self.port_ui_window.should_open_sell_goods_window:
                all_ui_windows.remove(self.port_ui_window)
                self.port_ui_window = None
                self.should_open_sell_goods_window = True

        if self.port_ui_window is not None:
            if self.port_ui_window.should_exit:
                all_ui_windows.remove(self.port_ui_window)
                self.port_ui_window = None

        if self.should_open_buy_goods_window and self.port_we_are_in is not None:
            self.should_open_buy_goods_window = False
            self.buy_goods_window = BuyGoodsWindow([312, 50, 400, 400], fonts, self, self.all_trade_goods,
                                                   self.port_we_are_in)
            all_ui_windows.append(self.buy_goods_window)

        if self.buy_goods_window is not None:
            if self.buy_goods_window.should_exit:
                all_ui_windows.remove(self.buy_goods_window)
                self.buy_goods_window = None
                if self.port_ui_window is None:
                    self.port_ui_window = PortUIWindow([437, 100, 150, 240], fonts, self.port_we_are_in, self)
                    all_ui_windows.append(self.port_ui_window)

        if self.should_open_sell_goods_window and self.port_we_are_in is not None:
            self.should_open_sell_goods_window = False
            self.sell_goods_window = SellGoodsWindow([312, 50, 400, 400], fonts, self, self.goods_in_hold,
                                                     self.port_we_are_in)
            all_ui_windows.append(self.sell_goods_window)

        if self.sell_goods_window is not None:
            if self.sell_goods_window.should_exit:
                all_ui_windows.remove(self.sell_goods_window)
                self.sell_goods_window = None
                if self.port_ui_window is None:
                    self.port_ui_window = PortUIWindow([437, 100, 150, 240], fonts, self.port_we_are_in,
                                                       self)
                    all_ui_windows.append(self.port_ui_window)

        if self.can_fire and self.right_mouse_held:
            self.reload_counter = 0.0
            self.can_fire = False
            mouse_world_pos = self.get_world_position_from_screen_pos(pygame.mouse.get_pos(),
                                                                      tiled_level.position_offset)
            new_target = mouse_world_pos
            x_dist = float(new_target[0]) - (float(self.position[0]))
            y_dist = float(new_target[1]) - (float(self.position[1]))
            distance = math.sqrt((x_dist ** 2) + (y_dist ** 2))
            if distance > 0.0:
                self.player_fire_target = new_target
                self.fire_vector = [x_dist / distance, y_dist / distance]

                # actually fire a bullet
                projectiles.append(
                    Cannonball(self, self.position, self.fire_vector, self.per_cannonball_damage))
                projectiles.append(Cannonball(self, [self.position[0] + (self.current_vector[0] * 16),
                                                     self.position[1] + (self.current_vector[1] * 16)],
                                              self.fire_vector, self.per_cannonball_damage))
                projectiles.append(Cannonball(self, [self.position[0] - (self.current_vector[0] * 16),
                                                     self.position[1] - (self.current_vector[1] * 16)],
                                              self.fire_vector, self.per_cannonball_damage))

        if not self.can_fire:
            self.reload_counter += time_delta
            if self.reload_counter > self.reload_time:
                self.can_fire = True

        if self.left_mouse_held:
            self.acceleration += (50.0 * time_delta)
            if self.acceleration > 100.0:
                self.acceleration = 100.0
            self.firing = False
            self.firing_timer = 0.0
            mouse_world_pos = self.get_world_position_from_screen_pos(pygame.mouse.get_pos(),
                                                                      tiled_level.position_offset)
            if self.playerMoveTarget != mouse_world_pos:
                new_target = mouse_world_pos
                x_dist = float(new_target[0]) - float(self.position[0])
                y_dist = float(new_target[1]) - float(self.position[1])
                distance = math.sqrt((x_dist * x_dist) + (y_dist * y_dist))
                if distance > 0.0:
                    self.playerMoveTarget = new_target
                    self.target_vector = [x_dist / distance, y_dist / distance]
                    self.target_angle = math.atan2(-self.target_vector[0], -self.target_vector[1]) * 180 / math.pi

                    # print("Target: " + str(self.targetAngle) + ", current: " + str(self.newFacingAngle))
        else:
            self.acceleration = 0.0

        if self.target_angle != self.new_facing_angle:
            if (self.new_facing_angle >= 0 and self.target_angle >= 0) or (
                    self.new_facing_angle <= 0 and self.target_angle <= 0):
                if self.new_facing_angle > self.target_angle:
                    self.new_facing_angle -= (90.0 * time_delta)
                    if self.new_facing_angle < self.target_angle:
                        self.new_facing_angle = self.target_angle
                else:
                    self.new_facing_angle += (90.0 * time_delta)
                    if self.new_facing_angle > self.target_angle:
                        self.new_facing_angle = self.target_angle
            else:
                if abs(self.new_facing_angle) < 90.0 and abs(self.target_angle) < 90.0:
                    if self.new_facing_angle > 0 > self.target_angle:
                        self.new_facing_angle -= (90.0 * time_delta)
                    elif self.new_facing_angle < 0 < self.target_angle:
                        self.new_facing_angle += (90.0 * time_delta)
                else:
                    if self.new_facing_angle > 0 > self.target_angle:
                        if self.new_facing_angle < 180:
                            self.new_facing_angle += (90.0 * time_delta)
                        else:
                            self.new_facing_angle = -180 + (self.new_facing_angle - 180)
                    elif self.new_facing_angle < 0 < self.target_angle:
                        if self.new_facing_angle > -180:
                            self.new_facing_angle -= (90.0 * time_delta)
                        else:
                            self.new_facing_angle = 180 - (self.new_facing_angle + 180)

            radians_angle = (self.new_facing_angle * math.pi) / 180
            self.current_vector = [-math.sin(radians_angle), -math.cos(radians_angle)]
            # print(str(self.currentVector) + " " + str(self.targetAngle))

        self.speed += self.acceleration + self.water_resistance * time_delta
        if self.speed > self.max_speed:
            self.speed = self.max_speed
        if self.speed < 0.0:
            self.speed = 0.0

        test_move_position = [0, 0]
        test_move_position[0] = self.position[0]
        test_move_position[1] = self.position[1]
        test_move_position[0] += (self.current_vector[0] * time_delta * self.speed)
        test_move_position[1] += (self.current_vector[1] * time_delta * self.speed)
        if not self.in_port:
            test_move_position[0] += (time_delta * wind.wind_vector[0] * 4.0 * abs(dot_wind))
            test_move_position[1] += (time_delta * wind.wind_vector[1] * 4.0 * abs(dot_wind))

        test_screen_position = [0, 0]
        test_screen_position[0] = test_move_position[0] - tiled_level.position_offset[0]
        test_screen_position[1] = test_move_position[1] - tiled_level.position_offset[1]

        self.test_collision_sprite.image = pygame.transform.rotate(self.original_image, self.new_facing_angle)
        self.test_collision_sprite.rect = self.sprite.image.get_rect()
        self.test_collision_sprite.rect.center = self.rot_point(
            [test_screen_position[0], test_screen_position[1] + self.sprite_rot_offset[1]], test_screen_position,
            -self.new_facing_angle)
        collided = False
        collided_obj_pos = [0, 0]
        collided_obj_radius = 0.0

        player_tile_pos = [int(test_move_position[0] / 64), int(test_move_position[1] / 64)]
        for tile_x in range(max(0, player_tile_pos[0] - 3), min(64, player_tile_pos[0] + 3)):
            for tile_y in range(max(0, player_tile_pos[1] - 3), min(64, player_tile_pos[1] + 3)):
                tile = tiled_level.tile_grid[tile_x][tile_y]
                if tile.collidable:
                    if tile.test_player_collision(self.test_collision_sprite.rect, self):
                        collided = True
                        collided_obj_pos[0] = tile.world_position[0]
                        collided_obj_pos[1] = tile.world_position[1]

                        x_dist = float(collided_obj_pos[0]) - float(test_move_position[0])
                        y_dist = float(collided_obj_pos[1]) - float(test_move_position[1])
                        distance_from_collided_tile = math.sqrt((x_dist ** 2) + (y_dist ** 2))
                        to_tile_vector = [x_dist / distance_from_collided_tile, y_dist / distance_from_collided_tile]
                        angle = math.atan2(to_tile_vector[0], to_tile_vector[1]) * 180 / math.pi
                        angle = abs(angle)
                        if angle > 90:
                            angle = angle - 90
                        if angle > 45:
                            angle = 90 - angle
                        lerp_value = angle / 45.0

                        max_dist = math.sqrt(32 ** 2 + 32 ** 2)
                        collided_obj_radius = self.lerp(32, max_dist, lerp_value)

        for monster in monsters:
            if self.test_monster_collision(self.test_collision_sprite.rect, monster):
                collided = True
                collided_obj_pos = monster.position
                collided_obj_radius = monster.collide_radius

        if collided:
            # handle collision with small bounce away from obstacle
            self.collide_col = pygame.Color(180, 80, 80)
            x_dist = float(collided_obj_pos[0]) - float(test_move_position[0])
            y_dist = float(collided_obj_pos[1]) - float(test_move_position[1])
            distance_from_collided_object = math.sqrt((x_dist ** 2) + (y_dist ** 2))
            to_object_vector = [x_dist / distance_from_collided_object, y_dist / distance_from_collided_object]

            overlap_distance = 1 + abs(collided_obj_radius - (distance_from_collided_object - self.collide_radius))
            self.position[0] -= (to_object_vector[0] * overlap_distance)
            self.position[1] -= (to_object_vector[1] * overlap_distance)
        else:
            self.collide_col = pygame.Color(180, 180, 180)
            self.position[0] += (self.current_vector[0] * time_delta * self.speed)
            self.position[1] += (self.current_vector[1] * time_delta * self.speed)
            if not self.in_port:
                self.position[0] += (time_delta * wind.wind_vector[0] * 4.0 * abs(dot_wind))
                self.position[1] += (time_delta * wind.wind_vector[1] * 4.0 * abs(dot_wind))

        self.update_screen_position(tiled_level.position_offset)

        self.circle1_centre = [self.screen_position[0] + (self.current_vector[0] * 16),
                               self.screen_position[1] + (self.current_vector[1] * 16)]
        self.circle2_centre = [self.screen_position[0] + (self.current_vector[0] * -16),
                               self.screen_position[1] + (self.current_vector[1] * -16)]
        self.circle3_centre = self.screen_position

        if not self.firing:
            self.sprite.image = pygame.transform.rotate(self.original_image, self.new_facing_angle)
            self.sprite.rect = self.sprite.image.get_rect()
            self.sprite.rect.center = self.rot_point(
                [self.screen_position[0], self.screen_position[1] + self.sprite_rot_offset[1]], self.screen_position,
                -self.new_facing_angle)

    def add_health(self, health):
        self.health += health
        if self.health > self.max_health:
            self.health = self.max_health

    def take_damage(self, damage):
        self.health -= damage.amount
        if self.health < 0:
            self.health = 0
        self.should_flash_sprite = True

    def test_projectile_collision(self, projectile_rect):  # screen space
        if self.sprite.rect.colliderect(projectile_rect):
            c1_tl = self.test_point_in_circle(projectile_rect.topleft, self.circle1_centre, self.collide_radius)
            c1_tr = self.test_point_in_circle(projectile_rect.topright, self.circle1_centre, self.collide_radius)
            c1_bl = self.test_point_in_circle(projectile_rect.bottomleft, self.circle1_centre, self.collide_radius)
            c1_br = self.test_point_in_circle(projectile_rect.bottomright, self.circle1_centre, self.collide_radius)
            if c1_tl or c1_tr or c1_bl or c1_br:
                return True
            c2_tl = self.test_point_in_circle(projectile_rect.topleft, self.circle2_centre, self.collide_radius)
            c2_tr = self.test_point_in_circle(projectile_rect.topright, self.circle2_centre, self.collide_radius)
            c2_bl = self.test_point_in_circle(projectile_rect.bottomleft, self.circle2_centre, self.collide_radius)
            c2_br = self.test_point_in_circle(projectile_rect.bottomright, self.circle2_centre, self.collide_radius)
            if c2_tl or c2_tr or c2_bl or c2_br:
                return True
            c3_tl = self.test_point_in_circle(projectile_rect.topleft, self.circle3_centre, self.collide_radius)
            c3_tr = self.test_point_in_circle(projectile_rect.topright, self.circle3_centre, self.collide_radius)
            c3_bl = self.test_point_in_circle(projectile_rect.bottomleft, self.circle3_centre, self.collide_radius)
            c3_br = self.test_point_in_circle(projectile_rect.bottomright, self.circle3_centre, self.collide_radius)
            if c3_tl or c3_tr or c3_bl or c3_br:
                return True
        return False

    def test_monster_collision(self, temp_player_rect, monster):
        collided = False
        if temp_player_rect.colliderect(monster.sprite.rect):
            collided = self.is_intersecting(monster)
        return collided

    @staticmethod
    def test_tile_collision(temp_player_rect, tile):
        collided = False
        if temp_player_rect.colliderect(tile.sprite.rect):
            collided = True  # self.isIntersectingTile(tile)
        return collided

    def test_pick_up_collision(self, pick_up_rect):
        collided = False
        if self.sprite.rect.colliderect(pick_up_rect):
            collided = True
        return collided

    @staticmethod
    def test_point_in_circle(point, circle_pos, circle_radius):
        return (point[0] - circle_pos[0]) ** 2 + (point[1] - circle_pos[1]) ** 2 < circle_radius ** 2

    # tiles positions are in screen space currently
    def is_intersecting_tile(self, c2):
        x_dist = (self.screen_position[0] - c2.position[0]) ** 2
        y_dist = (self.screen_position[1] - c2.position[1]) ** 2
        distance = math.sqrt(x_dist + y_dist)
        if abs((self.collide_radius - c2.collide_radius)) <= distance <= (self.collide_radius + c2.collide_radius):
            return True
        else:
            return False

    def is_intersecting(self, c2):
        distance = math.sqrt((self.position[0] - c2.position[0]) ** 2 + (self.position[1] - c2.position[1]) ** 2)
        if abs((self.collide_radius - c2.collide_radius)) <= distance <= (self.collide_radius + c2.collide_radius):
            return True
        else:
            return False

    def draw_collision_rect(self, screen):
        ck = (180, 100, 100)
        s = pygame.Surface((self.test_collision_sprite.rect.width, self.test_collision_sprite.rect.height))
        s.fill(ck)
        s.set_alpha(75)
        screen.blit(s, self.sprite.rect)

    def draw_collision_circles(self, screen):
        self.draw_radius_circle(screen, self.circle1_centre)
        self.draw_radius_circle(screen, self.circle2_centre)
        self.draw_radius_circle(screen, self.circle3_centre)

    def draw_radius_circle(self, screen, circle_center):
        ck = (127, 33, 33)
        int_position = [0, 0]
        int_position[0] = int(circle_center[0] - self.collide_radius)
        int_position[1] = int(circle_center[1] - self.collide_radius)
        s = pygame.Surface((self.collide_radius * 2, self.collide_radius * 2))

        # first, "erase" the surface by filling it with a color and
        # setting this color as colorkey, so the surface is empty
        s.fill(ck)
        s.set_colorkey(ck)

        pygame.draw.circle(s, self.collide_col, (self.collide_radius, self.collide_radius), self.collide_radius)

        # after drawing the circle, we can set the 
        # alpha value (transparency) of the surface
        s.set_alpha(75)
        screen.blit(s, int_position)

    @staticmethod
    def distance_from_line(point, line):

        x1 = line[0][0]
        y1 = line[0][1]
        x2 = line[1][0]
        y2 = line[1][1]
        x3 = point[0]
        y3 = point[1]

        px = x2 - x1
        py = y2 - y1

        something = px * px + py * py

        u = ((x3 - x1) * px + (y3 - y1) * py) / float(something)

        if u > 1:
            u = 1
        elif u < 0:
            u = 0

        x = x1 + u * px
        y = y1 + u * py

        dx = x - x3
        dy = y - y3

        # Note: If the actual distance does not matter,
        # if you only want to compare what this function
        # returns to other results of this function, you
        # can just return the squared distance instead
        # (i.e. remove the sqrt) to gain a little performance

        dist = math.sqrt(dx * dx + dy * dy)

        return dist

    @staticmethod
    def rot_point(point, axis, ang):
        """ Orbit. calculates the new loc for a point that rotates a given num of degrees around an axis point,
        +clockwise, -anticlockwise -> tuple x,y
        """
        ang -= 90
        x, y = point[0] - axis[0], point[1] - axis[1]
        radius = math.sqrt(x * x + y * y)  # get the distance between points

        r_ang = math.radians(ang)  # convert ang to radians.

        h = axis[0] + (radius * math.cos(r_ang))
        v = axis[1] + (radius * math.sin(r_ang))

        return [h, v]

    @staticmethod
    def lerp(a, b, c):
        return (c * b) + ((1.0 - c) * a)


class RespawnPlayer:
    def __init__(self, player):
        self.controlScheme = player.scheme

        self.respawnTimer = 2.0
        self.timeToSpawn = False
        self.hasRespawned = False

    def update(self, frame_time_ms):
        self.respawnTimer -= (frame_time_ms / 1000.0)
        if self.respawnTimer < 0.0:
            self.timeToSpawn = True


class PlayerScore:
    def __init__(self, screen_position):
        self.screenPosition = screen_position
        self.score = 0
