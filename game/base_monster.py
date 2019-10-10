import math
import random
import pygame

from game.cannonball import Cannonball


class MonsterPath:
    def __init__(self):
        self.startWaypoint = [0, 0]
        self.waypoints = []
        self.waypointRadius = 32


class BaseMonster:
    def __init__(self, start_pos, monster_id, loaded_image, point_cost, all_monster_sprites, tiled_level):

        self.id = monster_id
        self.point_cost = point_cost
        self.start_pos = start_pos
        self.tiled_level = tiled_level

        self.original_image = loaded_image
        self.image = self.original_image.copy()
        self.sprite = pygame.sprite.Sprite()
                       
        self.sprite.rect = self.image.get_rect()
        self.collide_radius = 20

        self.sprite.rect.center = self.start_pos

        self.position = [float(self.sprite.rect.center[0]), float(self.sprite.rect.center[1])]

        self.screen_position = [0, 0]
        self.screen_position[0] = self.position[0]
        self.screen_position[1] = self.position[1]

        self.update_screen_position(self.tiled_level.position_offset)
        
        self.sprite.image = self.image

        self.sprite.rect.center = self.screen_position

        self.change_direction_time = 5.0
        self.change_direction_accumulator = 0.0

        self.next_way_point = self.get_random_point_in_radius_of_point([500, 400], 96)

        x_dist = float(self.next_way_point[0]) - float(self.position[0])
        y_dist = float(self.next_way_point[1]) - float(self.position[1])
        self.distance_to_next_way_point = math.sqrt((x_dist ** 2) + (y_dist ** 2))
        self.current_vector = [x_dist / self.distance_to_next_way_point, y_dist / self.distance_to_next_way_point]
        self.current_angle = math.atan2(-self.current_vector[0], -self.current_vector[1]) * 180 / math.pi
        self.old_facing_angle = 0.0
        self.target_vector = [x_dist / self.distance_to_next_way_point, y_dist / self.distance_to_next_way_point]
        self.target_angle = math.atan2(-self.target_vector[0], -self.target_vector[1]) * 180 / math.pi

        self.sprite_rot_centre_offset = [0.0, 0.0]

        self.move_speed = 0.0
        self.attack_move_speed = 0.0
        self.idle_move_speed = 0.0
        self.rotate_speed = 60.0

        self.rotate_sprite()
    
        self.should_die = False
        
        self.sprite_needs_update = True
        self.all_monster_sprites = all_monster_sprites
        self.all_monster_sprites.add(self.sprite)

        self.health = 100

        self.slow_down_percentage = 1.0

        self.is_wandering_aimlessly = True
        self.random_target_change_time = random.uniform(3.0, 15.0)
        self.random_target_change_acc = 0.0

        self.time_to_home_in_on_player = False
        self.monster_home_on_target_time = random.uniform(0.2, 0.8)
        self.monster_home_on_target_acc = 0.0

        self.is_time_to_start_attack = True
        self.attackTimeAcc = 0.0
        self.attack_time_delay = 5.0

        self.is_attacking = False

        self.sprite_flash_acc = 0.0
        self.sprite_flash_time = 0.15
        self.should_flash_sprite = False

        self.flash_sprite = pygame.sprite.Sprite()

        self.player_distance = 1000

        self.found_target_range = 500.0
        self.cannon_range = 300.0
        self.lost_target_range = 800.0

        self.ai_tick_acc = random.uniform(0.0, 0.5)
        self.ai_tick_time = 0.5

        self.coll_radius_colour = pygame.Color(180, 180, 180)

        self.per_cannon_ball_damage = 20

        self.circle1_centre = [self.screen_position[0] + (self.current_vector[0] * 32),
                               self.screen_position[1] + (self.current_vector[1] * 32)]
        self.circle2_centre = [self.screen_position[0] + (self.current_vector[0] * -32),
                               self.screen_position[1] + (self.current_vector[1] * -32)]
        self.circle3_centre = self.screen_position

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
                rot_centre = self.rot_point([self.screen_position[0],
                                             self.screen_position[1] + self.sprite_rot_centre_offset[1]],
                                            self.screen_position, -self.current_angle)
                self.flash_sprite.rect.center = rot_centre
                all_sprites.add(self.flash_sprite)
        return all_sprites

    def attack(self, projectiles):
        fire_vector = [self.current_vector[1], -self.current_vector[0]]
        projectiles.append(Cannonball(self, self.position, fire_vector, self.per_cannon_ball_damage))
        projectiles.append(Cannonball(self, [self.position[0] + (self.current_vector[0] * 16),
                                             self.position[1] + (self.current_vector[1] * 16)],
                                      fire_vector, self.per_cannon_ball_damage))
        projectiles.append(Cannonball(self, [self.position[0] - (self.current_vector[0] * 16),
                                             self.position[1] - (self.current_vector[1] * 16)],
                                      fire_vector, self.per_cannon_ball_damage))

    def update_ai(self, player, projectiles):
        if self.is_wandering_aimlessly and not player.should_die:
            self.move_speed = self.idle_move_speed

            if self.player_distance < self.found_target_range:
                self.is_wandering_aimlessly = False
            elif self.random_target_change_acc > self.random_target_change_time:
                self.random_target_change_acc = 0.0
                self.random_target_change_time = random.uniform(3.0, 15.0)

                self.next_way_point = self.get_random_point_on_screen()

                x_dist = float(self.next_way_point[0]) - float(self.position[0])
                y_dist = float(self.next_way_point[1]) - float(self.position[1])
                self.distance_to_next_way_point = math.sqrt((x_dist * x_dist) + (y_dist * y_dist))
                self.target_vector = [x_dist / self.distance_to_next_way_point,
                                      y_dist / self.distance_to_next_way_point]
                self.target_angle = math.atan2(-self.target_vector[0], -self.target_vector[1]) * 180 / math.pi
            else:
                x_dist = float(self.next_way_point[0]) - float(self.position[0])
                y_dist = float(self.next_way_point[1]) - float(self.position[1])
                self.distance_to_next_way_point = math.sqrt((x_dist * x_dist) + (y_dist * y_dist))

        elif not self.is_wandering_aimlessly and not player.should_die:
            self.move_speed = self.attack_move_speed
            
            if self.monster_home_on_target_acc > self.monster_home_on_target_time:
                self.monster_home_on_target_acc = 0.0
                self.monster_home_on_target_time = random.uniform(0.3, 1.5)
                self.time_to_home_in_on_player = True

            if self.time_to_home_in_on_player:
                self.time_to_home_in_on_player = False

                if self.player_distance > self.lost_target_range:
                    self.is_wandering_aimlessly = True
                    self.coll_radius_colour = pygame.Color(180, 180, 180)
                elif self.player_distance > self.cannon_range:
                    self.coll_radius_colour = pygame.Color(80, 180, 80)
                    x_dist = float(player.position[0]) - float(self.position[0])
                    y_dist = float(player.position[1]) - float(self.position[1])
                    self.distance_to_next_way_point = math.sqrt(x_dist ** 2 + y_dist ** 2)
                    self.distance_to_next_way_point -= self.cannon_range
                    
                    self.target_vector = [x_dist / self.distance_to_next_way_point,
                                          y_dist / self.distance_to_next_way_point]
                    self.target_angle = math.atan2(-self.target_vector[0], -self.target_vector[1]) * 180 / math.pi
                else:  # we want to be side on to player as much as possible
                    self.coll_radius_colour = pygame.Color(180, 80, 80)
                    x_dist = float(player.position[0]) - float(self.position[0])
                    y_dist = float(player.position[1]) - float(self.position[1])
                    total_dist = math.sqrt(x_dist**2 + y_dist ** 2)
                    vector_to_player = [x_dist/total_dist, y_dist/total_dist]
                    broadside_vector = [-vector_to_player[1], vector_to_player[0]]
                    self.target_vector = broadside_vector
                    self.target_angle = math.atan2(-self.target_vector[0], -self.target_vector[1]) * 180 / math.pi
                    self.distance_to_next_way_point = 20.0  # just some random distance in front

            else:
                x_dist = float(player.position[0]) - float(self.position[0])
                y_dist = float(player.position[1]) - float(self.position[1])
                self.distance_to_next_way_point = (math.sqrt((x_dist ** 2) + (y_dist ** 2)))

            if self.attackTimeAcc > self.attack_time_delay:
                self.attackTimeAcc = 0.0
                self.is_time_to_start_attack = True
                
            if self.player_distance <= self.cannon_range and self.is_time_to_start_attack:
                self.is_time_to_start_attack = False
                self.is_attacking = True
            
        if self.is_attacking:
            self.is_attacking = False
            self.attack(projectiles)

    def update_movement_and_collision(self, time_delta, player, new_explosions,
                                      collidable_tiles, monsters, pick_up_spawner, wind, projectiles):
        player_x_dist = float(player.position[0]) - float(self.position[0])
        player_y_dist = float(player.position[1]) - float(self.position[1])
        self.player_distance = math.sqrt((player_x_dist ** 2) + (player_y_dist ** 2))
        
        for explosion in new_explosions:
            if self.test_explosion_collision(explosion):
                self.take_damage(explosion.damage)
        if self.health <= 0:
            self.should_die = True

        if self.ai_tick_acc > self.ai_tick_time:
            self.update_ai(player, projectiles)
            self.ai_tick_acc = 0.0
        else:
            self.ai_tick_acc += time_delta
            self.random_target_change_acc += time_delta
            self.monster_home_on_target_acc += time_delta
            self.attackTimeAcc += time_delta
            
        # rotate
        if self.target_angle != self.current_angle:
            if (self.current_angle >= 0 and self.target_angle >= 0) or\
                    (self.current_angle <= 0 and self.target_angle <= 0):
                if self.current_angle > self.target_angle:
                    self.current_angle -= (self.rotate_speed * time_delta)
                    if self.current_angle < self.target_angle:
                        self.current_angle = self.target_angle
                else:
                    self.current_angle += (self.rotate_speed * time_delta)
                    if self.current_angle > self.target_angle:
                        self.current_angle = self.target_angle
            else:
                if abs(self.current_angle) < 90.0 and abs(self.target_angle) < 90.0:
                    if self.current_angle > 0 > self.target_angle:
                            self.current_angle -= (self.rotate_speed * time_delta)
                    elif self.current_angle < 0 < self.target_angle:
                            self.current_angle += (self.rotate_speed * time_delta)
                else:
                    if self.current_angle > 0 > self.target_angle:
                        if self.current_angle < 180:
                            self.current_angle += (self.rotate_speed * time_delta)
                        else:
                            self.current_angle = -180 + (self.current_angle - 180)
                    elif self.current_angle < 0 < self.target_angle:
                        if self.current_angle > -180:
                            self.current_angle -= (self.rotate_speed * time_delta)
                        else:
                            self.current_angle = 180 - (self.current_angle + 180)

            radians_angle = (self.current_angle * math.pi) / 180
            self.current_vector = [-math.sin(radians_angle), -math.cos(radians_angle)]
            self.rotate_sprite()
        # move
        if self.distance_to_next_way_point > 3.0:

            test_move_position = [0, 0]
            test_move_position[0] = self.position[0]
            test_move_position[1] = self.position[1]
            test_move_position[0] += (self.current_vector[0] * time_delta * self.move_speed)
            test_move_position[1] += (self.current_vector[1] * time_delta * self.move_speed)

            direction_magnitude = max(0.00001, math.sqrt(self.current_vector[0] ** 2 + self.current_vector[1] ** 2))
            unit_dir_vector = [self.current_vector[0] / direction_magnitude,
                               self.current_vector[1] / direction_magnitude]
            dot_wind = unit_dir_vector[0] * wind.direction[0] + unit_dir_vector[1] * wind.direction[1]
            
            test_move_position[0] += (time_delta * wind.wind_vector[0] * 4.0 * abs(dot_wind))
            test_move_position[1] += (time_delta * wind.wind_vector[1] * 4.0 * abs(dot_wind))
            
            test_rect = self.sprite.image.get_rect()
            test_rect.center = test_move_position
            
            collided = False
            collided_obj_pos = [0, 0]
            collided_obj_radius = 0.0
            for tile in collidable_tiles:
                if self.test_tile_collision(test_rect, tile):
                    collided = True
                    collided_obj_pos = tile.position
                    collided_obj_radius = tile.collide_radius

            for monster in monsters:
                if monster != self:
                    if self.test_monster_collision(test_rect, monster):
                        collided = True
                        collided_obj_pos = monster.position
                        collided_obj_radius = monster.collide_radius

            if collided:
                # handle collision with small bounce away from obstacle
                if self.is_wandering_aimlessly:
                    self.random_target_change_acc = self.random_target_change_time
                x_dist = float(collided_obj_pos[0]) - float(self.position[0])
                y_dist = float(collided_obj_pos[1]) - float(self.position[1])
                distance_from_collided_tile = math.sqrt((x_dist * x_dist) + (y_dist * y_dist))
                to_tile_vector = [x_dist/distance_from_collided_tile, y_dist/distance_from_collided_tile]

                overlap = abs(distance_from_collided_tile - collided_obj_radius - self.collide_radius)
                overlap_distance = overlap + (time_delta * self.move_speed)
                self.position[0] -= (to_tile_vector[0] * overlap_distance)
                self.position[1] -= (to_tile_vector[1] * overlap_distance)
                if abs(self.current_vector[0] * time_delta * self.move_speed) > (to_tile_vector[0] * overlap_distance):
                    self.position[0] += (self.current_vector[0] * time_delta * self.move_speed)
                if abs(self.current_vector[1] * time_delta * self.move_speed) > (to_tile_vector[1] * overlap_distance):
                    self.position[1] += (self.current_vector[1] * time_delta * self.move_speed)

            else:
                    
                self.position[0] += (self.current_vector[0] * time_delta * self.move_speed)
                self.position[1] += (self.current_vector[1] * time_delta * self.move_speed)
                self.position[0] += (time_delta * wind.wind_vector[0] * 4.0 * abs(dot_wind))
                self.position[1] += (time_delta * wind.wind_vector[1] * 4.0 * abs(dot_wind))

        self.update_screen_position(self.tiled_level.position_offset)
        self.sprite.rect.center = self.screen_position

        self.circle1_centre = [self.screen_position[0] + (self.current_vector[0] * 32),
                               self.screen_position[1] + (self.current_vector[1] * 32)]
        self.circle2_centre = [self.screen_position[0] + (self.current_vector[0] * -32),
                               self.screen_position[1] + (self.current_vector[1] * -32)]
        self.circle3_centre = self.screen_position

        if self.should_die:
            self.all_monster_sprites.remove(self.flash_sprite)
            self.all_monster_sprites.remove(self.sprite)
            self.try_pick_up_spawn(pick_up_spawner)
            player.add_score(100)
            player.add_xp(25)

    def draw_collision_rect(self, screen):
        ck = (180, 100, 100)
        s = pygame.Surface((self.sprite.rect.width, self.sprite.rect.height))
        s.fill(ck)
        s.set_alpha(75)
        screen.blit(s, self.sprite.rect)

    def draw_collision_circles(self, screen):
        self.draw_radius_circle(screen, self.circle1_centre)
        self.draw_radius_circle(screen, self.circle2_centre)
        self.draw_radius_circle(screen, self.circle3_centre)
        
    def draw_radius_circle(self, screen, circle_centre):
        ck = (127, 33, 33)
        int_position = [0, 0]
        int_position[0] = int(circle_centre[0] - self.collide_radius)
        int_position[1] = int(circle_centre[1] - self.collide_radius)
        s = pygame.Surface((self.collide_radius * 2, self.collide_radius * 2))

        # first, "erase" the surface by filling it with a color and
        # setting this color as colorkey, so the surface is empty
        s.fill(ck)
        s.set_colorkey(ck)
        
        pygame.draw.circle(s, self.coll_radius_colour, (self.collide_radius, self.collide_radius), self.collide_radius)

        # after drawing the circle, we can set the 
        # alpha value (transparency) of the surface
        s.set_alpha(75)
        screen.blit(s, int_position)
            
    @staticmethod
    def get_random_point_in_radius_of_point(point, radius):
        t = 2 * math.pi * random.random()
        u = random.random() + random.random()
        if u > 1:
            r = 2-u
        else:
            r = u
        return [point[0] + radius * r * math.cos(t), point[1] + radius * r * math.sin(t)]

    def test_explosion_collision(self, explosion):
        collided = False
        if self.sprite.rect.colliderect(explosion.sprite.rect):
            collided = self.is_intersecting(explosion) or self.is_circle_inside(explosion)
        return collided
    
    @staticmethod
    def test_point_in_explosion(point, explosion):
        return (point[0] - explosion.position[0])**2 + (point[1] - explosion.position[1])**2 < explosion.radius**2

    def test_projectile_collision(self, projectile_rect):
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

    @staticmethod
    def test_point_in_circle(point, circle_pos, circle_radius):
        return (point[0] - circle_pos[0]) ** 2 + (point[1] - circle_pos[1]) ** 2 < circle_radius ** 2
    
    def test_monster_collision(self, temp_player_rect, monster):
        collided = False
        if temp_player_rect.colliderect(monster.sprite.rect):
            collided = self.is_intersecting(monster)
        return collided
    
    def test_tile_collision(self, temp_player_rect, tile):
        collided = False
        if temp_player_rect.colliderect(tile.sprite.rect):
            collided = self.is_intersecting(tile)
        return collided

    def is_intersecting(self, c2):
        distance = math.sqrt((self.position[0] - c2.position[0]) ** 2 + (self.position[1] - c2.position[1]) ** 2)
        if abs((self.collide_radius - c2.collide_radius)) <= distance <= (self.collide_radius + c2.collide_radius):
            return True
        else:
            return False

    def is_circle_inside(self, c2):
        distance = math.sqrt((self.position[0] - c2.position[0]) ** 2 + (self.position[1] - c2.position[1]) ** 2)
        if self.collide_radius < c2.collide_radius:
            is_inside = distance + self.collide_radius <= c2.collide_radius
        else:
            is_inside = distance + c2.collide_radius <= self.collide_radius
        return is_inside

    def set_average_speed(self, average_speed):
        self.move_speed = random.randint(int(average_speed * 0.75), int(average_speed * 1.25))
        return self.move_speed

    def take_damage(self, damage):
        self.health -= damage.amount
        self.should_flash_sprite = True

    def get_random_point_on_screen(self):
        random_tile = random.choice(self.tiled_level.walkable_tiles)
        return random_tile.world_position

    def update_screen_position(self, world_offset):
        self.screen_position[0] = self.position[0] - world_offset[0]
        self.screen_position[1] = self.position[1] - world_offset[1]

    def rotate_sprite(self):
        direction_magnitude = math.sqrt(self.current_vector[0] ** 2 + self.current_vector[1] ** 2)
        if direction_magnitude > 0.0:
            unit_dir_vector = [self.current_vector[0] / direction_magnitude,
                               self.current_vector[1] / direction_magnitude]
            self.old_facing_angle = math.atan2(-unit_dir_vector[0], -unit_dir_vector[1]) * 180 / math.pi
            monster_centre_position = self.sprite.rect.center
            self.image = pygame.transform.rotate(self.original_image, self.old_facing_angle)
            self.sprite.image = self.image
            self.sprite.rect = self.image.get_rect()
            self.sprite.rect.center = monster_centre_position

    def try_pick_up_spawn(self, pickup_spawner):
        pickup_spawner.try_spawn(self.position)

    @staticmethod
    def rot_point(point, axis, ang):
        """ Orbit. calculates the new loc for a point that rotates a given num of degrees around an axis point,
        +clockwise, -anticlockwise -> tuple x,y
        """
        ang -= 90
        x, y = point[0] - axis[0], point[1] - axis[1]
        radius = math.sqrt(x*x + y*y)  # get the distance between points

        r_ang = math.radians(ang)       # convert ang to radians.

        h = axis[0] + (radius * math.cos(r_ang))
        v = axis[1] + (radius * math.sin(r_ang))

        return [h, v]

    @staticmethod
    def lerp(a, b, c):
        return (c * b) + ((1.0-c) * a)
