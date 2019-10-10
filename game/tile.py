import pygame
import copy
import csv
import os


class AISpawn:
    def __init__(self, image, position, type_id):
        self.typeID = type_id
        self.position = [0, 0]
        self.position[0] = position[0]
        self.position[1] = position[1]

        self.world_position = [0, 0]
        self.world_position[0] = position[0]
        self.world_position[1] = position[1]
        self.tileImage = image
        self.sprite = pygame.sprite.Sprite()
        self.sprite.image = self.tileImage
        self.sprite.rect = self.tileImage.get_rect()
        self.sprite.rect.center = self.position

    def update_offset_position(self, offset):
        self.position[0] = self.world_position[0] - offset[0]
        self.position[1] = self.world_position[1] - offset[1]
        self.sprite.rect.center = self.position


class TileData:

    def __init__(self, file_path, tile_map):
        self.file_path = file_path
        self.tile_map = tile_map
        self.tile_id = os.path.splitext(os.path.basename(file_path))[0]
        self.collidable = False
        self.collide_radius = 26
        self.collision_shapes = []
        self.image_coords = (0, 0)
        self.tile_image = None

    def load_tile_data(self):
        if os.path.isfile(self.file_path):
            with open(self.file_path, "r") as tileFile:
                reader = csv.reader(tileFile)
                for line in reader:
                    data_type = line[0]
                    if data_type == "isCollidable":
                        self.collidable = bool(int(line[1]))
                    elif data_type == "tileImageCoords":
                        self.image_coords = (int(line[1]), int(line[2]))
                        self.tile_image = self.tile_map[int(line[1])][int(line[2])]
                    elif data_type == "rect":
                        top_left_tile_offset = [int(line[1]), int(line[2])]
                        self.collision_shapes.append(["rect", top_left_tile_offset,
                                                      pygame.Rect(int(line[1]), int(line[2]),
                                                                  int(line[3])-int(line[1]),
                                                                  int(line[4])-int(line[2]))])
                    elif data_type == "circle":
                        self.collision_shapes.append(["circle", [int(line[1]), int(line[2])],
                                                      [int(line[1]), int(line[2])], int(line[3])])
                        self.collide_radius = int(line[3])

    def copy(self):
        tile_data_copy = TileData(self.file_path,  self.tile_map)
        tile_data_copy.tile_id = copy.deepcopy(self.tile_id)
        tile_data_copy.collidable = copy.deepcopy(self.collidable)
        tile_data_copy.collide_radius = copy.deepcopy(self.collide_radius)
        tile_data_copy.collision_shapes = copy.deepcopy(self.collision_shapes)
        self.tile_image = self.tile_map[self.image_coords[0]][self.image_coords[1]]
        return tile_data_copy

        
class Tile:
    def __init__(self, position, tile_angle, tile_data, layer):
        self.group_tile_data = tile_data
        self.tile_data = tile_data.copy()
        self.world_position = [position[0], position[1]]
        self.position = [position[0], position[1]]
        self.angle = tile_angle
        self.collide_radius = self.group_tile_data.collide_radius
        self.collidable = self.group_tile_data.collidable
        self.tile_id = self.group_tile_data.tile_id
        self.tile_image = pygame.transform.rotate(self.group_tile_data.tile_image, self.angle)
        self.sprite = pygame.sprite.Sprite()
        self.sprite.image = self.tile_image
        self.sprite.rect = self.tile_image.get_rect()
        self.sprite.rect.center = self.position
        self.is_visible = False
        self.layer = layer

    def update_collision_shapes_position(self):
        for shape in self.tile_data.collision_shapes:
            if shape[0] == "rect":
                shape[2].left = self.sprite.rect.left + shape[1][0]
                shape[2].top = self.sprite.rect.top + shape[1][1]
            if shape[0] == "circle":
                shape[2][0] = self.sprite.rect.left + shape[1][0]
                shape[2][1] = self.sprite.rect.top + shape[1][1]

    def update_offset_position(self, offset, screen_data):
        should_update = False
        should_add_to_visible_tiles = False
        should_add_to_visible_collidable_tiles = False
        self.position[0] = self.world_position[0] - offset[0]
        self.position[1] = self.world_position[1] - offset[1]
        self.sprite.rect.center = self.position
        self.update_collision_shapes_position()
        if -32 <= self.position[0] <= screen_data.screen_size[0] + 32:
                if -32 <= self.position[1] <= screen_data.screen_size[1] + 32:
                    if not self.is_visible:
                        should_update = True
                    self.is_visible = True
                    should_add_to_visible_tiles = True
                    if self.collidable:
                        should_add_to_visible_collidable_tiles = True
                else:
                    self.is_visible = False
        else:
            self.is_visible = False
        return should_update, should_add_to_visible_tiles, should_add_to_visible_collidable_tiles
            
    def draw_collision_shapes(self, screen):
        for shape in self.tile_data.collision_shapes:
            if shape[0] == "circle":
                self.draw_radius_circle(screen, shape[2], shape[3])
            elif shape[0] == "rect":
                self.draw_collision_rect(screen, shape[2])

    @staticmethod
    def draw_collision_rect(screen, rect):
        ck = (180, 100, 100)
        s = pygame.Surface((rect.width, rect.height))
        s.fill(ck)
        s.set_alpha(75)
        screen.blit(s, rect)
        
    @staticmethod
    def draw_radius_circle(screen, centre, radius):
        ck = (127, 33, 33)
        int_position = [0, 0]
        int_position[0] = int(centre[0]-radius)
        int_position[1] = int(centre[1]-radius)
        s = pygame.Surface((radius*2, radius*2))

        # first, "erase" the surface by filling it with a color and
        # setting this color as colorkey, so the surface is empty
        s.fill(ck)
        s.set_colorkey(ck)

        pygame.draw.circle(s, pygame.Color(180, 100, 100), (radius, radius), radius)

        # after drawing the circle, we can set the 
        # alpha value (transparency) of the surface
        s.set_alpha(75)
        screen.blit(s, int_position)

    def test_projectile_collision(self, projectile_rect):  # screen space
        collided = False
        if self.sprite.rect.colliderect(projectile_rect):
            for collision_shape in self.tile_data.collision_shapes:
                if collision_shape[0] == "circle":
                    if self.test_rect_in_circle(projectile_rect, collision_shape[2], collision_shape[3]):
                        collided = True
                elif collision_shape[0] == "rect":
                    if collision_shape[2].colliderect(projectile_rect):
                        collided = True  

        return collided

    def test_player_collision(self, player_rect, player):  # screen space
        collided = False
        if self.sprite.rect.colliderect(player_rect):
            for collision_shape in self.tile_data.collision_shapes:
                if collision_shape[0] == "circle":
                    if self.test_rect_in_circle(player_rect, collision_shape[2], collision_shape[3]):
                        collided = True
                elif collision_shape[0] == "rect":
                    if self.test_rect_in_circle(collision_shape[2], player.test_collision_sprite.rect.center,
                                                player.collide_radius):
                        collided = True  

        return collided

    @staticmethod
    def test_point_in_circle(point, circle_pos, circle_radius):
        return (point[0] - circle_pos[0]) ** 2 + (point[1] - circle_pos[1]) ** 2 < circle_radius ** 2

    @staticmethod
    def test_rect_in_circle(rect, circle_centre, circle_radius):
        rect_half_width = rect.width/2
        rect_half_height = rect.height/2
        cx = abs(circle_centre[0] - rect.x - rect_half_width)
        x_dist = rect_half_width + circle_radius
        if cx > x_dist:
            return False
        cy = abs(circle_centre[1] - rect.y - rect_half_height)
        y_dist = rect_half_height + circle_radius
        if cy > y_dist:
            return False
        if cx <= rect_half_width or cy <= rect_half_height:
            return True
        x_corner_dist = cx - rect_half_width
        y_corner_dist = cy - rect_half_height
        x_corner_dist_sq = x_corner_dist * x_corner_dist
        y_corner_dist_sq = y_corner_dist * y_corner_dist
        max_corner_dist_sq = circle_radius ** 2
        return x_corner_dist_sq + y_corner_dist_sq <= max_corner_dist_sq
    
    def rotate_tile_right(self):
        self.angle -= 90
        if self.angle < 0:
            self.angle = 270
        self.tile_image = pygame.transform.rotate(self.tile_image, -90)
        self.sprite.image = self.tile_image

    def rotate_tile_left(self):
        self.angle += 90
        if self.angle > 270:
            self.angle = 0
        self.tile_image = pygame.transform.rotate(self.tile_image, 90)
        self.sprite.image = self.tile_image
